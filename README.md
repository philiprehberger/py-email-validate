# philiprehberger-email-validate

[![Tests](https://github.com/philiprehberger/py-email-validate/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-email-validate/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-email-validate.svg)](https://pypi.org/project/philiprehberger-email-validate/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-email-validate)](https://github.com/philiprehberger/py-email-validate/commits/main)

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

### Role-Based Email Detection

```python
from philiprehberger_email_validate import validate_email, is_role_based

result = validate_email("info@example.com")
print(result.is_role_based)  # True

is_role_based("admin@example.com")    # True
is_role_based("john@example.com")     # False
```

### Email Domain Suggestions

```python
from philiprehberger_email_validate import validate_email, suggest_domain

result = validate_email("user@gmial.com")
print(result.suggested_domain)  # "gmail.com"

suggest_domain("hotmial.com")   # "hotmail.com"
suggest_domain("gmail.com")     # "" (no suggestion needed)
```

### RFC 5321 Strict Mode

```python
from philiprehberger_email_validate import validate_email

result = validate_email("user@example.com", strict=True)
print(result.valid)  # True

result = validate_email(".user@example.com", strict=True)
print(result.valid)  # False
print(result.error)  # "Local part starts or ends with a dot (RFC 5321)"
```

### Bulk Validation

```python
from philiprehberger_email_validate import validate_many

results = validate_many(["user@example.com", "bad@@email", "test@gmail.com"])
for r in results:
    print(r.normalized, r.valid)

# With concurrent MX lookups and strict mode
results = validate_many(emails, check_mx=True, concurrent=True, strict=True)
```

### Extract Emails from Text

```python
from philiprehberger_email_validate import extract_emails

emails = extract_emails("Contact hello@example.com or support@test.org")
# ["hello@example.com", "support@test.org"]
```

### Email Parts

```python
from philiprehberger_email_validate import email_parts

parts = email_parts("user@example.com")
print(parts.local)   # "user"
print(parts.domain)  # "example.com"
print(parts.tld)     # "com"
```

### Mask Email

```python
from philiprehberger_email_validate import mask_email

mask_email("john@example.com")     # "j***n@example.com"
mask_email("alice@example.com")    # "a***e@example.com"
```

## API

| Function / Class | Description |
|------------------|-------------|
| `EmailResult` | Dataclass with `valid`, `normalized`, `domain`, `error`, `is_disposable`, `is_role_based`, and `suggested_domain` fields |
| `normalize(email)` | Normalize an email: lowercase, strip whitespace, Gmail dot-insensitivity, plus-addressing cleanup |
| `is_valid(email)` | Quick boolean syntax check |
| `validate_email(email, check_mx, extra_disposable, strict)` | Full validation returning an `EmailResult` |
| `validate_many(emails, check_mx, concurrent, extra_disposable, strict)` | Validate multiple emails with optional parallel MX lookups |
| `is_role_based(email)` | Check if an email uses a role-based local part (info@, admin@, etc.) |
| `suggest_domain(domain)` | Suggest a corrected domain for common typos |
| `set_disposable_domains(domains)` | Merge additional domains into the global disposable domains set |
| `DISPOSABLE_DOMAINS` | Mutable set of known disposable email domains |
| `ROLE_PREFIXES` | Frozen set of known role-based email prefixes |
| `COMMON_DOMAINS` | Frozen set of common email provider domains used for suggestions |
| `extract_emails(text)` | Extract all valid email addresses from text, deduplicated |
| `email_parts(email)` | Split email into structured parts (local, domain, tld, normalized) |
| `EmailParts` | Dataclass with `local`, `domain`, `tld`, `normalized` fields |
| `mask_email(email, mask_char, visible)` | Mask the local part for privacy display |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-email-validate)

🐛 [Report issues](https://github.com/philiprehberger/py-email-validate/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-email-validate/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
