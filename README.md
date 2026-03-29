# philiprehberger-email-validate

[![Tests](https://github.com/philiprehberger/py-email-validate/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-email-validate/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-email-validate.svg)](https://pypi.org/project/philiprehberger-email-validate/)
[![GitHub release](https://img.shields.io/github/v/release/philiprehberger/py-email-validate)](https://github.com/philiprehberger/py-email-validate/releases)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-email-validate)](https://github.com/philiprehberger/py-email-validate/commits/main)
[![License](https://img.shields.io/github/license/philiprehberger/py-email-validate)](LICENSE)
[![Bug Reports](https://img.shields.io/github/issues/philiprehberger/py-email-validate/bug)](https://github.com/philiprehberger/py-email-validate/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
[![Feature Requests](https://img.shields.io/github/issues/philiprehberger/py-email-validate/enhancement)](https://github.com/philiprehberger/py-email-validate/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

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

normalize("  User@Example.COM  ")          # "user@example.com"
normalize("first.last+tag@gmail.com")      # "firstlast@gmail.com"
normalize("user+promo@example.com")        # "user@example.com"
```

### MX Lookup

```python
from philiprehberger_email_validate import validate_email

result = validate_email("user@example.com", check_mx=True)
if not result.valid:
    print(result.error)  # "MX lookup failed for domain: example.com"
```

### Disposable Email Detection

```python
from philiprehberger_email_validate import validate_email

result = validate_email("user@mailinator.com")
print(result.is_disposable)  # True
```

### Custom Disposable Domains

```python
from philiprehberger_email_validate import validate_email, set_disposable_domains

# Per-call extra domains
result = validate_email("user@tempmail.xyz", extra_disposable=["tempmail.xyz"])
print(result.is_disposable)  # True

# Global merge with built-in list
set_disposable_domains({"tempmail.xyz", "fakeemail.org"})
```

### Bulk Validation

```python
from philiprehberger_email_validate import validate_many

results = validate_many(["user@example.com", "bad@@email", "test@gmail.com"])
for r in results:
    print(r.normalized, r.valid)

# With concurrent MX lookups
results = validate_many(emails, check_mx=True, concurrent=True)
```

## API

| Function / Class | Description |
|------------------|-------------|
| `EmailResult` | Dataclass with `valid`, `normalized`, `domain`, `error`, and `is_disposable` fields |
| `normalize(email)` | Normalize an email: lowercase, strip whitespace, Gmail dot-insensitivity, plus-addressing cleanup |
| `is_valid(email)` | Quick boolean syntax check |
| `validate_email(email, check_mx, extra_disposable)` | Full validation returning an `EmailResult` |
| `validate_many(emails, check_mx, concurrent, extra_disposable)` | Validate multiple emails with optional parallel MX lookups |
| `set_disposable_domains(domains)` | Merge additional domains into the global disposable domains set |
| `DISPOSABLE_DOMAINS` | Mutable set of known disposable email domains |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this package useful, consider giving it a star on GitHub — it helps motivate continued maintenance and development.

[![LinkedIn](https://img.shields.io/badge/Philip%20Rehberger-LinkedIn-0A66C2?logo=linkedin)](https://www.linkedin.com/in/philiprehberger)
[![More packages](https://img.shields.io/badge/more-open%20source%20packages-blue)](https://philiprehberger.com/open-source-packages)

## License

[MIT](LICENSE)
