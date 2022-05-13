"""Tests for philiprehberger_email_validate."""

from __future__ import annotations

from philiprehberger_email_validate import (
    DISPOSABLE_DOMAINS,
    EmailResult,
    is_valid,
    normalize,
    set_disposable_domains,
    validate_email,
    validate_many,
)


# --- is_valid ---


def test_valid_email() -> None:
    assert is_valid("user@example.com") is True


def test_invalid_email_no_at() -> None:
    assert is_valid("userexample.com") is False


def test_invalid_email_double_at() -> None:
    assert is_valid("user@@example.com") is False


def test_invalid_email_no_domain() -> None:
    assert is_valid("user@") is False


def test_is_valid_accepts_plus_addressing() -> None:
    assert is_valid("user+tag@example.com") is True


def test_is_valid_rejects_spaces() -> None:
    assert is_valid("user @example.com") is False


# --- normalize ---


def test_normalize_strips_whitespace() -> None:
    assert normalize("  User@Example.COM  ") == "user@example.com"


def test_normalize_lowercases() -> None:
    assert normalize("Alice@Bob.ORG") == "alice@bob.org"


def test_normalize_gmail_dot_insensitivity() -> None:
    assert normalize("first.last@gmail.com") == "firstlast@gmail.com"


def test_normalize_gmail_dot_insensitivity_googlemail() -> None:
    assert normalize("first.last@googlemail.com") == "firstlast@googlemail.com"


def test_normalize_non_gmail_keeps_dots() -> None:
    assert normalize("first.last@example.com") == "first.last@example.com"


def test_normalize_plus_addressing_removal() -> None:
    assert normalize("user+tag@example.com") == "user@example.com"


def test_normalize_plus_addressing_gmail() -> None:
    assert normalize("first.last+promo@gmail.com") == "firstlast@gmail.com"


def test_normalize_no_at_returns_lowered() -> None:
    assert normalize("  NOTANEMAIL  ") == "notanemail"


# --- validate_email ---


def test_validate_email_returns_email_result() -> None:
    result = validate_email("test@example.com")
    assert isinstance(result, EmailResult)
    assert result.valid is True
    assert result.normalized == "test@example.com"
    assert result.domain == "example.com"
    assert result.error == ""


def test_validate_email_invalid_syntax() -> None:
    result = validate_email("not-an-email")
    assert result.valid is False
    assert result.error == "Invalid email syntax"


def test_validate_email_normalizes_input() -> None:
    result = validate_email("  Test@EXAMPLE.com  ")
    assert result.normalized == "test@example.com"
    assert result.valid is True


def test_validate_email_disposable_detection() -> None:
    result = validate_email("user@mailinator.com")
    assert result.is_disposable is True


def test_validate_email_non_disposable() -> None:
    result = validate_email("user@gmail.com")
    assert result.is_disposable is False


def test_validate_email_extra_disposable() -> None:
    result = validate_email("user@mytemp.xyz", extra_disposable=["mytemp.xyz"])
    assert result.is_disposable is True


def test_validate_email_extra_disposable_no_side_effect() -> None:
    """extra_disposable should not permanently modify DISPOSABLE_DOMAINS."""
    before = len(DISPOSABLE_DOMAINS)
    validate_email("user@unique-temp-1234.xyz", extra_disposable=["unique-temp-1234.xyz"])
    assert len(DISPOSABLE_DOMAINS) == before


def test_validate_email_gmail_normalized() -> None:
    result = validate_email("first.last+tag@gmail.com")
    assert result.normalized == "firstlast@gmail.com"
    assert result.valid is True


# --- set_disposable_domains ---


def test_set_disposable_domains_adds() -> None:
    before = len(DISPOSABLE_DOMAINS)
    set_disposable_domains({"custom-disposable-test.com"})
    assert "custom-disposable-test.com" in DISPOSABLE_DOMAINS
    assert len(DISPOSABLE_DOMAINS) == before + 1
    # Cleanup
    DISPOSABLE_DOMAINS.discard("custom-disposable-test.com")


def test_set_disposable_domains_lowercases() -> None:
    set_disposable_domains({"UPPER-TEMP.COM"})
    assert "upper-temp.com" in DISPOSABLE_DOMAINS
    # Cleanup
    DISPOSABLE_DOMAINS.discard("upper-temp.com")


# --- validate_many ---


def test_validate_many_basic() -> None:
    results = validate_many(["user@example.com", "bad@@email", "test@gmail.com"])
    assert len(results) == 3
    assert results[0].valid is True
    assert results[1].valid is False
    assert results[2].valid is True


def test_validate_many_with_extra_disposable() -> None:
    results = validate_many(
        ["user@mydisposable.xyz", "user@example.com"],
        extra_disposable=["mydisposable.xyz"],
    )
    assert results[0].is_disposable is True
    assert results[1].is_disposable is False


def test_validate_many_non_concurrent() -> None:
    results = validate_many(
        ["user@example.com", "bad@@email"],
        concurrent=False,
    )
    assert len(results) == 2
    assert results[0].valid is True
    assert results[1].valid is False
