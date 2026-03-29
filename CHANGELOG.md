# Changelog

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
