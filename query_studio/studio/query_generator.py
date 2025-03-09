import json
import typing as t
import warnings

from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.output_parsers.string import StrOutputParser
from studio.defaults import DEFAULT_TABLE_DESCRIPTIONS, DEFAULT_TABLE_SCHEMA
from studio.models import Question
from studio.prompts import NL_QUESTION_GENERATOR_PROMPT, QUERY_OPTIMIZATION_PROMPT
from studio.utils import load_env
from tqdm import tqdm


class QueryGenerator:
    def __init__(
        self,
        llm: BaseLanguageModel,
        model: t.Optional[str] = None,
        api_key: t.Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the QueryGenerator with the specified language model, model name, and API key.

        Args:
            llm (BaseLanguageModel): The language model to use for generating queries.
            model (t.Optional[str]): The model name to use for generating queries.
            api_key (t.Optional[str]): The API key for authentication.
            **kwargs: Additional keyword arguments.
        """

        if llm is None:
            env = load_env()
            model = model if model else env.get("ANTHROPIC_MODEL")
            api_key = api_key if api_key else env.get("ANTHROPIC_API_KEY")

            if not model or not api_key:
                raise ValueError(
                    "Model and API key must be provided either as arguments or in the environment file."
                )
            self.llm = ChatAnthropic(model=model, api_key=api_key)
        else:
            self.llm = llm

        self.max_retries = kwargs.get("max_retries", 3)
        self._build_chains()

    def _build_chains(self) -> None:
        """
        Build the chains for generating natural language questions and optimizing queries.
        """
        self.generator_chain = (
            NL_QUESTION_GENERATOR_PROMPT | self.llm | StrOutputParser()
        )

        self.optimizer_chain = QUERY_OPTIMIZATION_PROMPT | self.llm | StrOutputParser()

    @staticmethod
    async def _generate_with_retry(
        chain: t.Any, input_dict: t.Dict[str, t.Any], max_retries: int
    ) -> t.Any:
        """
        Generate results with retry mechanism.

        Args:
            chain (t.Any): The chain to use for generation.
            input_dict (t.Dict[str, t.Any]): The input dictionary for the chain.
            max_retries (int): The maximum number of retries.

        Returns:
            t.Any: The generated results.
        """
        retries = 0
        while retries <= max_retries:
            try:
                return await chain.ainvoke(input_dict)
            except Exception as e:
                retries += 1
                print(f"Retrying...{retries}")
                if retries > max_retries:
                    raise Exception(f"Error processing question: {e}")

    def fit(self, table_descriptions: str = None, table_schema: str = None) -> None:
        """
        Fit the QueryGenerator with table descriptions and schema.

        Args:
            table_descriptions (str): Descriptions of the tables.
            table_schema (str): Schema of the tables.
        """
        if (table_descriptions is None) or (table_schema is None):
            warnings.warn(
                "No table descriptions or schema provided. Using default values."
            )

        self.table_descriptions = (
            table_descriptions if table_descriptions else DEFAULT_TABLE_DESCRIPTIONS
        )
        self.table_schema = table_schema if table_schema else DEFAULT_TABLE_SCHEMA

    async def generate_nl_questions(self, n: str) -> t.List[Question]:
        """
        Generate natural language questions.

        Args:
            n (str): The number of questions to generate.

        Returns:
            t.List[Question]: A list of generated questions.
        """
        input_dict = dict(
            table_description=self.table_descriptions,
            table_schema=self.table_schema,
            n_questions=n,
        )

        results = await self._generate_with_retry(
            self.generator_chain, input_dict, self.max_retries
        )

        results = json.loads(results)

        return [
            Question(question=q.pop("question"), metadata=q)
            for q in results.get("questions")
        ]

    async def optimize_query(
        self, questions: t.Union[t.List[str], t.List[Question]]
    ) -> t.List[Question]:
        """
        Optimize the given questions for SQL conversion.

        Args:
            questions (t.Union[t.List[str], t.List[Question]]): The questions to optimize.

        Returns:
            t.List[Question]: A list of optimized questions.
        """

        revised_questions = []

        for question in tqdm(questions):
            if isinstance(question, Question):
                q = question.question
                metadata = question.metadata
            elif isinstance(question, str):
                q = question
                metadata = {}

            input_dict = dict(
                table_descriptions=self.table_descriptions,
                table_schema=self.table_schema,
                question=q,
            )

            results = await self._generate_with_retry(
                self.optimizer_chain, input_dict, self.max_retries
            )

            results = json.loads(results)

            revised_questions.append(
                Question(
                    question=results.pop("optimized_question"),
                    metadata={**results, "nl_question": q, **metadata},
                )
            )

        return revised_questions
