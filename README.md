Here’s a sample `README.md` markdown file for your GitHub repository that explains the purpose and usage of your environment variable parsing script using the `Env` class with robust data validation via Pydantic.

---

# Env Parser with Pydantic Validation

This Python script provides a robust and customizable environment variable parser, leveraging **Pydantic** for data validation and type casting. It allows you to load, validate, and convert environment variables from a `.env` file into strongly typed values (e.g., integers, floats, dates, lists) with the ability to add custom parsers for additional flexibility.

## Features

- **Automatic Parsing**: Supports automatic parsing of common types like `str`, `int`, `float`, `bool`, `date`, `timedelta`, `uuid`, `json`, and more.
- **Custom Parsers**: Easily register custom parsers for specific environment variables.
- **Pydantic Validation**: All built-in parsers are powered by Pydantic for validation, ensuring robustness and correctness of the parsed data.
- **Error Handling**: Custom `EnvParseError` exception ensures clear and consistent error messages when parsing fails.

## Supported Parsers

- **String** (`str`)
- **Integer** (`int`)
- **Float** (`float`)
- **Boolean** (`bool`)
- **Date** (`date`) – Supports customizable date formats.
- **Timedelta** (`timedelta`)
- **UUID** (`uuid`)
- **JSON** (`json`)
- **Path** (`pathlib.Path`)
- **URL** (`urllib.parse.ParseResult`)
- **List** (comma-separated string into a list)
- **Dictionary** (comma-separated key:value pairs)
- **Base64 decoding** (including decoding to a Pillow image)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/env-parser.git
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   Required dependencies include:
   - `pydantic`: For data validation.
   - `python-dotenv`: (Optional) If you want to load `.env` files automatically.
   - `Pillow`: For handling base64-encoded images.

## Usage

1. **Loading Environment Variables:**

   Create a `.env` file in your project root:

   ```bash
   DB_HOST=127.0.0.1
   PORT=8080
   IS_ACTIVE=true
   TODAY=12-10-2024
   UUID=550e8400-e29b-41d4-a716-446655440000
   SAMPLE_JSON={"key": "value"}
   ```

2. **Using the `Env` Class:**

   ```python
   from env_parser import Env

   # Initialize the Env class with the .env file
   env = Env(env_file='.env')

   # Parse the environment variables
   db_host = env.str('DB_HOST')
   port = env.int('PORT')
   is_active = env.bool('IS_ACTIVE')
   today = env.date('TODAY', date_format='%d-%m-%Y')
   uuid_value = env.uuid('UUID')
   sample_json = env.json('SAMPLE_JSON')

   print(f"Database Host: {db_host}, Port: {port}, Active: {is_active}, Date: {today}, UUID: {uuid_value}")
   ```

3. **Custom Parsers:**

   You can define custom parsers for variables that require specific handling:

   ```python
   # Register a custom parser for a date field
   env.register_parser('CUSTOM_DATE', lambda x: datetime.strptime(x, '%Y-%m-%d').date())
   
   custom_date = env.date('CUSTOM_DATE')
   print(f"Custom Date: {custom_date}")
   ```

4. **Error Handling:**

   If parsing fails (e.g., invalid data type or format), an `EnvParseError` is raised with a detailed message. This ensures that you can catch and handle invalid environment variables effectively.

   ```python
   try:
       port = env.int('INVALID_PORT')
   except EnvParseError as e:
       print(f"Error: {str(e)}")
   ```

## Testing

This repository includes comprehensive `pytest` test cases to ensure correctness and prevent regressions. To run the tests:

1. Install `pytest` if you haven't already:

   ```bash
   pip install pytest
   ```

2. Run the tests:

   ```bash
   pytest test_env_parser.py
   ```

## Contributions

Contributions, bug reports, and feature requests are welcome! Please open an issue or submit a pull request to contribute to this project.

## License

This project is licensed under the MIT License.

---

Feel free to customize it further to fit your project specifics! You can add sections like "Known Issues" or "Future Enhancements" if relevant.