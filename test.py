import pytest
from datetime import datetime, timedelta
import uuid
from pyenv_parser import Env, EnvParseError  # assuming the Env class is saved as `env_parser.py`

@pytest.fixture
def mock_env_file(tmp_path):
    """Fixture to create a mock .env file."""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "DB_HOST=127.0.0.1\n"
        "TODAY=12-10-2024\n"
        "IS_ACTIVE=true\n"
        "PORT=8080\n"
        "UUID=550e8400-e29b-41d4-a716-446655440000\n"
        "SAMPLE_JSON={\"key\": \"value\"}\n"
        "SAMPLE_LIST=1,2,3\n"
        "SAMPLE_DICT=key1:value1,key2:value2\n"
        "BASE64_IMAGE=aGVsbG8gd29ybGQ=\n"
    )
    return env_file


@pytest.fixture
def env(mock_env_file):
    """Fixture to initialize the Env class."""
    return Env(env_file=str(mock_env_file))


def test_str(env):
    assert env.str("DB_HOST") == "127.0.0.1"


def test_int(env):
    assert env.int("PORT") == 8080


def test_bool(env):
    assert env.bool("IS_ACTIVE") is True


def test_date(env):
    assert env.date("TODAY", "%d-%m-%Y") == datetime(2024, 10, 12).date()


def test_uuid(env):
    assert env.uuid("UUID") == uuid.UUID("550e8400-e29b-41d4-a716-446655440000")


def test_json(env):
    assert env.json("SAMPLE_JSON") == {"key": "value"}


def test_list(env):
    assert env.list("SAMPLE_LIST") == ["1", "2", "3"]


def test_dict(env):
    assert env.dict("SAMPLE_DICT") == {"key1": "value1", "key2": "value2"}


def test_base64_decode(env):
    decoded = env.base64_decode("BASE64_IMAGE")
    assert decoded == b"hello world"


def test_custom_parser(env):
    # Register a custom parser for a specific key
    env.register_parser("TODAY", lambda x: datetime.strptime(x, "%d-%m-%Y").strftime("%Y-%m-%d"))
    assert env.str("TODAY") == "2024-10-12"


def test_port_validation(env):
    assert env.port("PORT") == 8080

    # Test invalid port number
    with pytest.raises(EnvParseError):
        env.register_parser("PORT", lambda x: "99999")  # Invalid port
        env.port("PORT")


def test_invalid_int(env):
    # Test an invalid integer parsing
    with pytest.raises(EnvParseError):
        env.register_parser("PORT", lambda x: "invalid")
        env.int("PORT")


def test_invalid_date_format(env):
    # Test an invalid date format
    with pytest.raises(EnvParseError):
        env.date("TODAY", "%Y/%m/%d")


def test_invalid_json(env):
    with pytest.raises(EnvParseError):
        env.register_parser("SAMPLE_JSON", lambda x: "invalid json")
        env.json("SAMPLE_JSON")


def test_invalid_base64(env):
    with pytest.raises(EnvParseError):
        env.register_parser("BASE64_IMAGE", lambda x: "invalid_base64")
        env.base64_decode("BASE64_IMAGE")


def test_invalid_uuid(env):
    with pytest.raises(EnvParseError):
        env.register_parser("UUID", lambda x: "invalid_uuid")
        env.uuid("UUID")


def test_timdelta(env):
    # Create a new key and validate parsing as timedelta
    env.env_values["TIMEDELTA"] = "3600"  # 1 hour in seconds
    assert env.timedelta("TIMEDELTA") == timedelta(seconds=3600)

    # Test invalid timedelta
    with pytest.raises(EnvParseError):
        env.env_values["TIMEDELTA"] = "invalid"
        env.timedelta("TIMEDELTA")


def test_missing_key(env):
    # Test missing key error handling
    with pytest.raises(EnvParseError):
        env.str("MISSING_KEY")


def test_custom_parsers_combined(env):
    # Test multiple custom parsers together

    # Custom UUID parser
    env.register_parser("CUSTOM_UUID", lambda x: uuid.UUID(x))
    env.env_values["CUSTOM_UUID"] = "550e8400-e29b-41d4-a716-446655440000"
    assert env.str("CUSTOM_UUID") == uuid.UUID("550e8400-e29b-41d4-a716-446655440000")

    # Custom date parser that returns date as string
    env.register_parser("CUSTOM_DATE", lambda x: datetime.strptime(x, "%d-%m-%Y").strftime("%Y-%m-%d"))
    env.env_values["CUSTOM_DATE"] = "15-10-2024"
    assert env.str("CUSTOM_DATE") == "2024-10-15"

def test_pydantic_validation(env):
    # Test built-in Pydantic validation for integers
    with pytest.raises(EnvParseError):
        env.register_parser("PORT", lambda x: "not an integer")
        env.int("PORT")

