import asyncio
import traceback
import typing as t

import pandas as pd
import psycopg2
from langchain.agents import create_sql_agent
from langchain.agents.agent import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.utilities import SQLDatabase
from langchain_anthropic import ChatAnthropic
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_core.language_models.base import BaseLanguageModel
from studio.defaults import DEFAULT_TABLE_COLUMNS
from studio.models import Question
from studio.utils import get_db_config
from tqdm import tqdm


def get_db(config: t.Dict[str, t.Any]) -> SQLDatabase:
    """
    Create a SQLDatabase instance from the given configuration.

    Args:
        config (Dict[str, Any]): Database configuration.

    Returns:
        SQLDatabase: An instance of SQLDatabase.
    """

    DB_URI = (
        "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    ).format(**config)

    sql_database = SQLDatabase.from_uri(
        DB_URI, engine_args={"connect_args": {"options": "-c search_path=gold"}}
    )
    return sql_database


class Text2SQLAgent:
    def __init__(
        self,
        llm: ChatAnthropic,
        config: t.Optional[t.Dict[str, str]] = None,
        table_columns: t.Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the Text2SQLAgent.

        Args:
            llm (ChatAnthropic): Language model instance.
            config (Dict[str, Any]): Database configuration.
        """

        if config is None:
            self.db_config: t.Dict[str, str] = get_db_config()

        self.db: SQLDatabase = get_db(config=self.db_config)
        self.llm: BaseLanguageModel = llm
        self.agent_executor: AgentExecutor = self._get_sql_agent_executor(
            self.db, self.llm
        )
        self.table_columns = table_columns if table_columns else DEFAULT_TABLE_COLUMNS

    @staticmethod
    def _get_sql_agent_executor(
        db: SQLDatabase, llm: BaseLanguageModel
    ) -> AgentExecutor:
        """
        Create a SQL agent executor.

        Args:
            db (SQLDatabase): SQLDatabase instance.
            llm (ChatAnthropic): Language model instance.

        Returns:
            Any: SQL agent executor.
        """
        agent_executor: AgentExecutor = create_sql_agent(
            llm=llm,
            toolkit=SQLDatabaseToolkit(db=db, llm=llm),
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            agent_executor_kwargs=dict(
                handle_parsing_errors=True,  # Add this line to handle parsing errors,
                return_intermediate_steps=True,
            ),
        )
        return agent_executor

    def ensure_gold_schema(self, sql_code: str) -> str:
        """
        Ensure `gold.` prefix in SQL code.

        Args:
            sql_code (str): SQL code.

        Returns:
            str: SQL code with enforced schema.
        """
        if " FROM " in sql_code and "gold." not in sql_code:
            sql_code = sql_code.replace(" FROM ", " FROM gold.")
        return sql_code

    async def generate_sql_from_text(
        self, questions: t.Union[t.List[str], t.List[Question]]
    ) -> t.List[t.Dict[str, t.Any]]:
        """
        Generate SQL code and chain of thought for a given question or list of questions.

        Args:
            questions (Union[str, List[str]]): User question or list of questions.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing input question, SQL code, chain of thought, output, and data.
        """

        results = []

        for question in tqdm(questions):
            if isinstance(question, Question):
                question = question.question
            if isinstance(question, str):
                question = question

            result: t.Dict[str,] = await self._generate_sql_and_chain_of_thought(
                question
            )
            results.append(result)

        return results

    async def _generate_sql_and_chain_of_thought(
        self, query: str
    ) -> t.Dict[str, t.Any]:
        """
        Generate SQL code and chain of thought for a given query.

        Args:
            query (str): User query.

        Returns:
            Dict[str, Any]: Dictionary containing input query, SQL code, chain of thought, output, and data.
        """
        prompt = (
            f"Generate SQL code for the following user query using the schema `gold` and the defined columns: {self.table_columns}.\n"
            f"User query: {query}\n"
            "Please provide the output in the following format:\n"
            "Action 1: Generate SQL\n"
            "Action Input 1: [Your SQL code here]"
            "Action Output: [Your Chain of Thought here]"
        )

        try:
            response = await self.agent_executor.ainvoke(prompt)

            steps = self.get_chain_of_thoughts(response)
            sql_code = self.get_sql_from_steps(steps)

            if "```" in sql_code:
                sql_code = sql_code.strip("```sql").strip("```")

            return {
                "input": query,
                "sql_code": sql_code,
                "chain_of_thought": steps,
                "output": response["output"],
                "data": self.get_data_from_sql(sql_code),
            }

        except asyncio.TimeoutError as e:
            return {
                "input": query,
                "error": "Query input might be too complex for our implementation and handling it is not yet supported."
                + str(e),
                "exception_type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }
        except Exception as e:
            return {
                "input": query,
                "error": str(e),
                "exception_type": type(e).__name__,
                "traceback": traceback.format_exc(),
            }

    @staticmethod
    def get_chain_of_thoughts(
        response: t.Dict[str, t.Any],
    ) -> t.List[t.Dict[str, t.Any]]:
        """
        Extract chain of thoughts from the response.

        Args:
            response (Dict[str, Any]): Response from the agent executor.

        Returns:
            List[Dict[str, Any]]: List of steps in the chain of thought.
        """
        steps = [
            {
                "action": "sql_generation",
                "input": response["input"],
                "output": response["intermediate_steps"][0][0].tool_input,
            }
        ]

        for step in response["intermediate_steps"]:
            action, output = step
            thought = {
                "action": action.tool,
                "input": action.tool_input,
                "output": output,
            }
            steps.append(thought)

        steps.append(
            {
                "action": "answer_generation",
                "input": response["intermediate_steps"][-1][1],
                "output": response["output"],
            }
        )
        return steps

    @staticmethod
    def get_sql_from_steps(steps: t.List[t.Dict[str, t.Any]]) -> str:
        """
        Extract SQL code from the steps.

        Args:
            steps (List[Dict[str, Any]]): List of steps in the chain of thought.

        Returns:
            str: SQL code.
        """
        for step in steps:
            if step["action"] == "sql_db_query":
                return step["input"]

    def get_data_from_sql(self, sql_code: str) -> t.Dict[str, t.Union[int, float, str]]:
        """
        Execute SQL code and return the result as a DataFrame.

        Args:
            sql_code (str): SQL code.

        Returns:
            Union[pd.DataFrame, Dict[str, Any]]: DataFrame containing the result or a dictionary with error information.
        """
        with psycopg2.connect(
            **self.db_config, options="-c search_path=gold"
        ) as connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "SET search_path TO gold;"
                    )  # Explicitly set search path
                    cursor.execute(sql_code)
                    columns = (
                        [desc[0] for desc in cursor.description]
                        if cursor.description
                        else []
                    )
                    rows = cursor.fetchall() if columns else []

                    if rows:
                        try:
                            df = pd.DataFrame(rows, columns=columns)
                            return df.head().to_dict(orient="records")
                        except Exception as e:
                            return {
                                "error": "Failed to convert rows to DataFrame",
                                "exception_type": type(e).__name__,
                                "traceback": traceback.format_exc(),
                                "input": rows,
                            }
                    else:
                        return {}

            except Exception as e:
                return {
                    "error": str(e),
                    "exception_type": type(e).__name__,
                    "input": sql_code,
                    "traceback": traceback.format_exc(),
                }
