# Project Setup

This guide will help you set up a virtual environment, install dependencies, and load API keys using `load_dotenv`.

## Prerequisites

- Python 3.x installed on your machine
- `pip` (Python package installer)

## Step 1: Create a Virtual Environment

1. Open your terminal.
2. Navigate to your project directory:
    ```sh
    cd /path/to/your/project/query-studio
    ```
3. Create a virtual environment:
    ```sh
    python3 -m venv venv
    ```
4. Activate the virtual environment:
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```

## Step 2: Install Dependencies

1. Ensure your virtual environment is activated.
2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Step 3: Load API Keys using `load_dotenv`

1. Install `python-dotenv` if it's not already included in your `requirements.txt`:
    ```sh
    pip install python-dotenv
    ```
2. Create a `.env` file in the root of your project directory and add your API keys:
    ```env
    DB_HOST="your_db_host_here"
    DB_PORT=your_db_port_here"
    DB_DATABASE="your_db_name_here"
    DB_USER_NAME="your_db_username_here"
    DB_USER_PASSWORD="your_db_password_here"
    ANTHROPIC_API_KEY="your_anthropic_api_key_here"
    ANTHROPIC_MODEL="your_anthropic_model_here"
    ```

    > **Note:** We only support Anthropic for now.

3. Load the environment variables in your Python script:
    ```python
    from dotenv import load_dotenv
    import os

    load_dotenv()

    api_key = os.getenv('API_KEY')
    another_key = os.getenv('ANOTHER_KEY')
    ```

## Step 4: Refer to `query_studio.ipynb`

For more detailed steps on how to use the Query Studio library, please refer to the `query_studio.ipynb` notebook included in the project.

## Conclusion

You have now set up a virtual environment, installed dependencies, and loaded API keys using `load_dotenv`. You are ready to start working on your project!
