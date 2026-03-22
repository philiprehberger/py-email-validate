# philiprehberger-email-validate

[![Tests](https://github.com/philiprehberger/py-email-validate/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-email-validate/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-email-validate.svg)](https://pypi.org/project/philiprehberger-email-validate/)
[![License](https://img.shields.io/github/license/philiprehberger/py-email-validate)](LICENSE)

Email validation with syntax checking and normalization.

## Installation

```bash
pip install philiprehberger-email-validate
```

## Usage

```python
from philiprehberger_email_validate import validate_email

result = validate_email("user@example.com")
print(result.valid)       # True
print(result.normalized)  # "user@example.com"
print(result.domain)      # "example.com"
```

### Quick Syntax Check

```python
from philiprehberger_email_validate import is_valid

is_valid("user@example.com")   # True
is_valid("not-an-email")       # False
```

### Normalization

```python
from philiprehberger_email_validate import normalize

normalize("  User@Example.COM  ")  # "user@example.com"
```

### MX Lookup

```python
from philiprehberger_email_validate import validate_email

result = validate_email("user@example.com", check_mx=True)
if not result.valid:
    print(result.error)  # "MX lookup failed for domain: example.com"
```

## API

| Function / Class | Description |
|------------------|-------------|
| `EmailResult` | Dataclass with `valid`, `normalized`, `domain`, and `error` fields |
| `normalize(email)` | Strip whitespace and lowercase an email address |
| `is_valid(email)` | Quick boolean syntax check |
| `validate_email(email, check_mx=False)` | Full validation returning an `EmailResult` |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
