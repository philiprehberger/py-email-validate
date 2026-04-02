"""Tests for philiprehberger_email_validate."""

from __future__ import annotations

from philiprehberger_email_validate import (
    COMMON_DOMAINS,
    DISPOSABLE_DOMAINS,
    ROLE_PREFIXES,
    EmailResult,
    is_role_based,
    is_valid,
    normalize,
    set_disposable_domains,
    suggest_domain,
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


def test_validate_many_with_strict() -> None:
    results = validate_many(
        ["user@example.com", ".bad@example.com"],
        strict=True,
    )
    assert results[0].valid is True
    assert results[1].valid is False


def test_validate_many_preserves_order() -> None:
    emails = ["a@example.com", "b@example.com", "c@example.com"]
    results = validate_many(emails)
    assert [r.normalized for r in results] == emails


# --- is_role_based ---


def test_is_role_based_info() -> None:
    assert is_role_based("info@example.com") is True


def test_is_role_based_admin() -> None:
    assert is_role_based("admin@example.com") is True


def test_is_role_based_support() -> None:
    assert is_role_based("support@example.com") is True


def test_is_role_based_postmaster() -> None:
    assert is_role_based("postmaster@example.com") is True


def test_is_role_based_noreply() -> None:
    assert is_role_based("noreply@example.com") is True
    assert is_role_based("no-reply@example.com") is True


def test_is_role_based_sales() -> None:
    assert is_role_based("sales@example.com") is True


def test_is_role_based_webmaster() -> None:
    assert is_role_based("webmaster@example.com") is True


def test_is_role_based_regular_user() -> None:
    assert is_role_based("john@example.com") is False


def test_is_role_based_personal_name() -> None:
    assert is_role_based("alice.smith@example.com") is False


def test_is_role_based_case_insensitive() -> None:
    assert is_role_based("ADMIN@example.com") is True


def test_is_role_based_with_plus_tag() -> None:
    assert is_role_based("info+tag@example.com") is True


def test_is_role_based_no_at_sign() -> None:
    assert is_role_based("notanemail") is False


def test_is_role_based_in_validate_email() -> None:
    result = validate_email("info@example.com")
    assert result.is_role_based is True
    assert result.valid is True


def test_not_role_based_in_validate_email() -> None:
    result = validate_email("john@example.com")
    assert result.is_role_based is False


# --- suggest_domain ---


def test_suggest_domain_gmail_typo() -> None:
    assert suggest_domain("gmial.com") == "gmail.com"


def test_suggest_domain_gmail_typo_gmal() -> None:
    assert suggest_domain("gmal.com") == "gmail.com"


def test_suggest_domain_hotmail_typo() -> None:
    assert suggest_domain("hotmial.com") == "hotmail.com"


def test_suggest_domain_yahoo_typo() -> None:
    assert suggest_domain("yahooo.com") == "yahoo.com"


def test_suggest_domain_outlook_typo() -> None:
    assert suggest_domain("outlok.com") == "outlook.com"


def test_suggest_domain_exact_match_no_suggestion() -> None:
    assert suggest_domain("gmail.com") == ""


def test_suggest_domain_unknown_domain_no_suggestion() -> None:
    assert suggest_domain("mycompany.com") == ""


def test_suggest_domain_case_insensitive() -> None:
    assert suggest_domain("GMIAL.COM") == "gmail.com"


def test_suggest_domain_strips_whitespace() -> None:
    assert suggest_domain("  gmial.com  ") == "gmail.com"


def test_suggest_domain_in_validate_email() -> None:
    result = validate_email("user@gmial.com")
    assert result.suggested_domain == "gmail.com"
    assert result.valid is True


def test_no_suggestion_in_validate_email() -> None:
    result = validate_email("user@gmail.com")
    assert result.suggested_domain == ""


# --- RFC 5321 strict mode ---


def test_strict_valid_email() -> None:
    result = validate_email("user@example.com", strict=True)
    assert result.valid is True
    assert result.error == ""


def test_strict_rejects_leading_dot_local() -> None:
    result = validate_email(".user@example.com", strict=True)
    assert result.valid is False
    assert "dot" in result.error.lower() or "RFC 5321" in result.error


def test_strict_rejects_trailing_dot_local() -> None:
    result = validate_email("user.@example.com", strict=True)
    assert result.valid is False
    assert "RFC 5321" in result.error


def test_strict_rejects_consecutive_dots() -> None:
    result = validate_email("us..er@example.com", strict=True)
    assert result.valid is False
    assert "Consecutive dots" in result.error


def test_strict_local_part_length() -> None:
    long_local = "a" * 65
    result = validate_email(f"{long_local}@example.com", strict=True)
    assert result.valid is False
    assert "64 characters" in result.error


def test_strict_local_part_max_length_ok() -> None:
    local_64 = "a" * 64
    result = validate_email(f"{local_64}@example.com", strict=True)
    assert result.valid is True


def test_strict_domain_label_too_long() -> None:
    long_label = "a" * 64
    result = validate_email(f"user@{long_label}.com", strict=True)
    assert result.valid is False
    assert "label" in result.error.lower() or "RFC 5321" in result.error


def test_strict_false_is_lenient() -> None:
    # Leading dot fails strict but passes lenient (basic regex doesn't reject it
    # because the basic regex allows dots in local)
    result = validate_email("us..er@example.com", strict=False)
    # Basic regex may or may not accept this; the point is strict=False doesn't
    # run the additional RFC 5321 checks
    assert result.error != "Consecutive dots in local part (RFC 5321)"


def test_strict_combined_with_disposable() -> None:
    result = validate_email("user@mailinator.com", strict=True)
    assert result.valid is True
    assert result.is_disposable is True


def test_strict_combined_with_role_based() -> None:
    result = validate_email("admin@example.com", strict=True)
    assert result.valid is True
    assert result.is_role_based is True


# --- EmailResult fields ---


def test_email_result_defaults() -> None:
    result = EmailResult(valid=True, normalized="a@b.com", domain="b.com")
    assert result.error == ""
    assert result.is_disposable is False
    assert result.is_role_based is False
    assert result.suggested_domain == ""


def test_email_result_all_fields() -> None:
    result = validate_email("info@gmial.com")
    assert isinstance(result.is_role_based, bool)
    assert isinstance(result.suggested_domain, str)
    assert isinstance(result.is_disposable, bool)


# --- ROLE_PREFIXES constant ---


def test_role_prefixes_contains_expected() -> None:
    expected = {"info", "admin", "support", "postmaster", "webmaster", "sales", "noreply"}
    assert expected.issubset(ROLE_PREFIXES)


# --- COMMON_DOMAINS constant ---


def test_common_domains_contains_major_providers() -> None:
    expected = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"}
    assert expected.issubset(COMMON_DOMAINS)
