from langchain_core.prompts import PromptTemplate

NL_QUESTION_GENERATOR_PROMPT_TEMPLATE = """You are helping generate authentic business questions focused solely on descriptive analytics that an analyst or business owner would ask. These questions should reflect real business needs for understanding historical performance and current states, not predictions or prescriptions.

Role Context:
1. Business Owner Perspective:
   - Wants to understand what has happened in the business
   - Needs summaries of performance metrics
   - Interested in key trends and patterns in historical data
   - Seeks to understand current business state

2. Analyst Perspective:
   - Focuses on data aggregation and summarization
   - Creates reports showing what has occurred
   - Identifies notable patterns in historical data
   - Organizes and categorizes past performance

Table Information:
{table_description}

Available Data (Schema):
{table_schema}

Generate {n_questions} natural business questions focused ONLY on descriptive analytics. For each question:
1. Write it as a real person would ask it in conversation
2. Focus ONLY on describing past data or current states (what happened/what is)
3. Make it specific to the business context
4. Ensure it's answerable with the available historical data
5. Add the role (Owner/Analyst) with each question

Descriptive Analytics Focus:
- Questions that summarize past performance
- Questions about data frequency and distribution
- Questions identifying patterns in historical data
- Questions comparing past periods or categories
- Questions about current state metrics
- Questions about "what happened" or "what is"

Do NOT include questions about:
- Predictive analytics (future forecasting)
- Prescriptive analytics (what should be done)
- Diagnostic analytics (deep causes of problems)
- Hypothetical scenarios

Bad examples (not descriptive or too technical):
- "What will our sales be next month?"
- "What should we do to improve delivery times?"
- "What is the COUNT of orders GROUP BY fulfillment_method?"
- "If we changed our pricing, what would happen?"

Good examples (descriptive and natural):
- "How did our online orders compare to in-store sales last quarter?"
- "What's our busiest day of the week based on the past three months?"
- "Which products have been our top sellers so far this year?"
- "What's the breakdown of our current sales by fulfillment method?"


Return in JSON format:
{{
    "questions": [
        {{
            "question": "natural language question about what happened or what is",
            "business_context": "the business situation this question helps understand"
            "role": "Owner or Analyst"
        }}
    ]
}}
""".strip()

QUERY_OPTIMIZATION_PROMPT_TEMPLATE = """
You are a SQL expert tasked with optimizing natural language business questions for automatic SQL generation. Your goal is to rephrase questions to be SQL-friendly while preserving the original intent.

Context about the database:
{table_descriptions}

Database Schema:
{table_schema}

User Question: {question}

First, analyze if this question can be answered with the available data schema.

Then, rephrase the question to make it optimized for SQL conversion by:
1. Using exact table and column names from the schema
2. Making implicit joins explicit (e.g., "for each product's sales" → "join product_sales with products")
3. Clarifying aggregation functions (e.g., "how many" → "count", "average" → "average")
4. Specifying grouping criteria (e.g., "by city", "by date")
5. Making filters explicit (e.g., "online orders" → "where fulfillment_method = 'PICKUP' or 'DELIVERY'")
6. Preserving time ranges mentioned in the original question
7. Using appropriate table based on the analysis needs (summary vs. detailed)

If the original question is vague or unclear, select the most reasonable interpretation based on the business context.

Return ONLY the optimized question in this JSON format:
{{
    "optimized_question": "Your SQL-friendly rephrased question"
}}

Do NOT include explanations or reasoning in your response, ONLY the JSON with the optimized question.

Examples:

Original: "How are our online sales doing?"
{{
    "optimized_question": "Calculate the sum of net_sales from orders table where stripe_tendered is not null, grouped by date"
}}

Original: "Which products sell best in each city?"
{{
    "optimized_question": "Find the products with highest count and sum of net_sales from orders_itemized joined with orders, grouped by product_type and city"
}}

Original: "What's our gift card usage like?"
{{
    "optimized_question": "Calculate the sum of gift_cards_purchased and gift_cards_tendered from orders table, grouped by order_time by month"
}}
""".strip()

NL_QUESTION_GENERATOR_PROMPT = PromptTemplate.from_template(
    NL_QUESTION_GENERATOR_PROMPT_TEMPLATE
)
QUERY_OPTIMIZATION_PROMPT = PromptTemplate.from_template(
    QUERY_OPTIMIZATION_PROMPT_TEMPLATE
)
