# Changelog

## 0.4.0 (2026-04-01)

- Add email domain typo suggestions via `suggest_domain()` with built-in list of common providers
- Add role-based email detection via `is_role_based()` for addresses like info@, admin@, support@
- Add RFC 5321 strict mode with `strict` parameter on `validate_email()` and `validate_many()`
- Add `is_role_based` and `suggested_domain` fields to `EmailResult` dataclass
- Add `ROLE_PREFIXES` and `COMMON_DOMAINS` constants to public API

## 0.3.1 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility

## 0.3.0 (2026-03-28)

- Add custom disposable domain list support via `extra_disposable` parameter and `set_disposable_domains()` function
- Add email normalization for Gmail dot-insensitivity, plus-addressing cleanup, and lowercase
- Add `concurrent` parameter to `validate_many()` for controlling parallel MX lookups
- Update README with new feature documentation and compliance fixes

## 0.2.0 (2026-03-27)

- Add `validate_many()` for bulk email validation with parallel MX lookups
- Add `DISPOSABLE_DOMAINS` set with ~50 common disposable email providers
- Add `is_disposable` field to `EmailResult` dataclass
- Add 8 badges to README (tests, PyPI, release, last updated, license, bugs, features, sponsor)
- Add Support section to README
- Add `.github/` templates (bug report, feature request, PR template, dependabot)

## 0.1.1 (2026-03-22)

- Add Changelog URL to project URLs
- Add `#readme` anchor to Homepage URL
- Add pytest and mypy configuration

## 0.1.0 (2026-03-21)

- Initial release
- Email syntax validation against RFC 5322 basic rules
- Email normalization (strip whitespace, lowercase)
- Optional MX record lookup with DNS fallback
