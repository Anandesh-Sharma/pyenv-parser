import json
import uuid
import base64
from typing import Callable, Any, Dict, List
from datetime import datetime, timedelta, date
from pathlib import Path
from urllib.parse import ParseResult, urlparse
from PIL import Image
from io import BytesIO
from pydantic import BaseModel, validator, conint, conlist, Field


class EnvParseError(Exception):
    """Custom exception for environment parsing errors."""
    pass


class Env(BaseModel):
    env_values: Dict[str, str] = Field(default_factory=dict)
    custom_parsers: Dict[str, Callable[[str], Any]] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    @validator("env_values", pre=True, always=True)
    def _load_env_file(cls, env_values, values, **kwargs) -> Dict[str, str]:
        """Load the environment file and return the key-value pairs."""
        env_file = values.get('env_file', '.env')
        env_dict: Dict[str, str] = {}
        try:
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env_dict[key] = value
            return env_dict
        except FileNotFoundError:
            raise EnvParseError(f"Env file {env_file} does not exist")

    def _get(self, key: str) -> str:
        """Helper method to get the environment variable or raise an error."""
        if key not in self.env_values:
            raise EnvParseError(f"{key} not found in environment variables")
        return self.env_values[key]

    def _apply_custom_parser(self, key: str, value: str) -> Any:
        """Applies a custom parser if one is registered for the given key."""
        if key in self.custom_parsers:
            return self.custom_parsers[key](value)
        return value  # If no custom parser, return the original value

    def register_parser(self, key: str, parser_func: Callable[[str], Any]) -> None:
        """
        Registers a custom parser function for a specific environment variable.

        :param key: The environment variable key
        :param parser_func: A function that takes a string input and returns the parsed output
        """
        if not callable(parser_func):
            raise EnvParseError(f"Provided parser for {key} is not callable")
        self.custom_parsers[key] = parser_func

    def str(self, key: str) -> str:
        """Parse the value as a string, applying custom parser if available."""
        value = self._get(key)
        return self._apply_custom_parser(key, value)

    def int(self, key: str) -> int:
        """Parse the value as an integer."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        try:
            return conint()(int(value))
        except ValueError:
            raise EnvParseError(f"Value {value} for {key} is not a valid integer")

    def float(self, key: str) -> float:
        """Parse the value as a float."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        try:
            return float(value)
        except ValueError:
            raise EnvParseError(f"Value {value} for {key} is not a valid float")

    def bool(self, key: str) -> bool:
        """Parse the value as a boolean."""
        value = self._get(key).lower()
        value = self._apply_custom_parser(key, value)
        if value in ['true', '1', 'yes']:
            return True
        elif value in ['false', '0', 'no']:
            return False
        raise EnvParseError(f"Value {value} for {key} is not a valid boolean")

    def date(self, key: str, date_format: str = '%d-%m-%Y') -> date:
        """Parse the value as a date."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            raise EnvParseError(f"Value {value} for {key} is not a valid date. Expected format: {date_format}")

    def timedelta(self, key: str) -> timedelta:
        """Parse the value as a timedelta."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        try:
            return timedelta(seconds=int(value))
        except ValueError:
            raise EnvParseError(f"Value {value} for {key} is not a valid timedelta")

    def uuid(self, key: str) -> uuid.UUID:
        """Parse the value as a UUID."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        try:
            return uuid.UUID(value)
        except ValueError:
            raise EnvParseError(f"Value {value} for {key} is not a valid UUID")

    def json(self, key: str) -> Any:
        """Parse the value as JSON."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise EnvParseError(f"Value {value} for {key} is not valid JSON")

    def path(self, key: str) -> Path:
        """Parse the value as a pathlib.Path."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        return Path(value)

    def url(self, key: str) -> ParseResult:
        """Parse the value as a valid URL."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        parsed = urlparse(value)
        if all([parsed.scheme, parsed.netloc]):
            return parsed
        raise EnvParseError(f"Value {value} for {key} is not a valid URL")

    def enum(self, key: str, enum_type: Any) -> Any:
        """Parse the value as an Enum type."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        try:
            return enum_type[value]
        except KeyError:
            raise EnvParseError(f"Value {value} for {key} is not a valid enum option for {enum_type}")

    def list(self, key: str, delimiter: str = ',') -> List[str]:
        """Parse the value as a list of strings."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        return [item.strip() for item in value.split(delimiter)]

    def dict(self, key: str) -> Dict[str, str]:
        """Parse the value as a dictionary."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        try:
            return dict(item.split(":") for item in value.split(","))
        except Exception:
            raise EnvParseError(f"Value {value} for {key} is not a valid dictionary format")

    def base64_decode(self, key: str) -> bytes:
        """Parse and decode a base64 string."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        try:
            return base64.b64decode(value)
        except ValueError:
            raise EnvParseError(f"Value {value} for {key} is not valid base64 encoded data")

    def base64_image(self, key: str) -> Image.Image:
        """Parse a base64-encoded image and return a Pillow Image object."""
        decoded = self.base64_decode(key)
        try:
            return Image.open(BytesIO(decoded))
        except Exception as e:
            raise EnvParseError(f"Error loading image from base64 data: {e}")

    def port(self, key: str) -> int:
        """Parse the value as a valid port number."""
        value = self._get(key)
        value = self._apply_custom_parser(key, value)
        port = self.int(key)
        if 1 <= port <= 65535:
            return port
        raise EnvParseError(f"Value {value} for {key} is not a valid port number")


# Example usage:
# Initialize the Env class
env = Env(env_file='.env')

# Register a custom parser for date in a different format
env.register_parser('CUSTOM_DATE', lambda x: datetime.strptime(x, '%Y/%m/%d').date())

# Fetch values with type casting
db_host = env.str('DB_HOST')
today_date = env.date('TODAY')
is_active = env.bool('IS_ACTIVE')
custom_date = env.str('CUSTOM_DATE')

port = env.port('PORT')

print(f"DB Host: {db_host}, Today: {today_date}, Is Active: {is_active}, Custom Date: {custom_date}, Port: {port}")
