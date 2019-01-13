"""Tests for philiprehberger_email_validate."""

from __future__ import annotations

from philiprehberger_email_validate import (
    EmailResult,
    is_valid,
    normalize,
    validate_email,
)


def test_valid_email() -> None:
    assert is_valid("user@example.com") is True


def test_invalid_email_no_at() -> None:
    assert is_valid("userexample.com") is False


def test_invalid_email_double_at() -> None:
    assert is_valid("user@@example.com") is False


def test_invalid_email_no_domain() -> None:
    assert is_valid("user@") is False


def test_normalize_strips_whitespace() -> None:
    assert normalize("  User@Example.COM  ") == "user@example.com"


def test_normalize_lowercases() -> None:
    assert normalize("Alice@Bob.ORG") == "alice@bob.org"


def test_is_valid_accepts_plus_addressing() -> None:
    assert is_valid("user+tag@example.com") is True


def test_is_valid_rejects_spaces() -> None:
    assert is_valid("user @example.com") is False


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
