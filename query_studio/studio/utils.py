import os
from typing import Dict


def load_env_variable(var_name: str) -> str:
    """
    Load an environment variable.

    Args:
        var_name (str): The name of the environment variable to load.

    Returns:
        str: The value of the environment variable.

    Raises:
        EnvironmentError: If the environment variable is not found.
    """
    value = os.getenv(var_name)
    if value is None:
        raise OSError(f"Environment variable {var_name} not found.")
    return value


def load_env() -> Dict[str, str]:
    """
    Load all environment variables.

    Returns:
        Dict[str, str]: A dictionary containing all environment variables.
    """
    return dict(os.environ)


def get_db_config() -> Dict[str, str]:
    """
    Get the database configuration from environment variables.

    Returns:
        Dict[str, str]: A dictionary containing the database configuration.
    """
    db_config = {
        "host": load_env_variable("DB_HOST"),
        "port": load_env_variable("DB_PORT"),
        "user": load_env_variable("DB_USER_NAME"),
        "password": load_env_variable("DB_USER_PASSWORD"),
        "database": load_env_variable("DB_DATABASE"),
    }

    return db_config
