"""Email validation with syntax checking and normalization."""

from __future__ import annotations

import concurrent.futures as _futures
import re
import socket
from dataclasses import dataclass, field

__all__ = [
    "EmailResult",
    "normalize",
    "is_valid",
    "validate_email",
    "validate_many",
    "set_disposable_domains",
    "DISPOSABLE_DOMAINS",
]

_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

_BUILTIN_DISPOSABLE_DOMAINS: frozenset[str] = frozenset({
    "mailinator.com",
    "guerrillamail.com",
    "tempmail.com",
    "throwaway.email",
    "yopmail.com",
    "sharklasers.com",
    "grr.la",
    "guerrillamailblock.com",
    "pokemail.net",
    "spam4.me",
    "dispostable.com",
    "maildrop.cc",
    "discard.email",
    "mailnesia.com",
    "tempail.com",
    "tempr.email",
    "temp-mail.org",
    "fakeinbox.com",
    "mintemail.com",
    "trashmail.com",
    "trashmail.me",
    "trashmail.net",
    "mailcatch.com",
    "mytemp.email",
    "mohmal.com",
    "burnermail.io",
    "guerrillamail.info",
    "guerrillamail.net",
    "guerrillamail.org",
    "guerrillamail.de",
    "harakirimail.com",
    "mailexpire.com",
    "mailforspam.com",
    "safetymail.info",
    "binkmail.com",
    "spamgourmet.com",
    "getairmail.com",
    "filzmail.com",
    "inboxalias.com",
    "jetable.org",
    "mailnull.com",
    "cuvox.de",
    "armyspy.com",
    "dayrep.com",
    "einrot.com",
    "fleckens.hu",
    "gustr.com",
    "jourrapide.com",
    "rhyta.com",
    "superrito.com",
    "teleworm.us",
    "tempinbox.com",
    "trash-mail.com",
})

DISPOSABLE_DOMAINS: set[str] = set(_BUILTIN_DISPOSABLE_DOMAINS)

# Gmail-style domains that ignore dots in the local part
_DOT_INSENSITIVE_DOMAINS: frozenset[str] = frozenset({
    "gmail.com",
    "googlemail.com",
})


def set_disposable_domains(domains: set[str]) -> None:
    """Merge additional domains into the disposable domains list.

    The provided domains are added to the built-in list. To reset,
    call with an empty set after clearing ``DISPOSABLE_DOMAINS``.

    Args:
        domains: Set of domain strings to add.
    """
    DISPOSABLE_DOMAINS.update(d.lower().strip() for d in domains)


@dataclass
class EmailResult:
    """Result of an email validation check."""

    valid: bool
    normalized: str
    domain: str
    error: str = field(default="")
    is_disposable: bool = field(default=False)


def normalize(email: str) -> str:
    """Normalize an email address.

    Handles:
    - Whitespace stripping and lowercasing
    - Gmail dot-insensitivity (removes dots from local part for gmail.com/googlemail.com)
    - Plus-addressing cleanup (removes ``+tag`` portion from local part)

    Args:
        email: The email address to normalize.

    Returns:
        The normalized email string.
    """
    cleaned = email.strip().lower()

    if "@" not in cleaned:
        return cleaned

    local, domain = cleaned.rsplit("@", 1)

    # Remove plus-addressing tag
    if "+" in local:
        local = local.split("+", 1)[0]

    # Gmail dot-insensitivity: remove dots from local part
    if domain in _DOT_INSENSITIVE_DOMAINS:
        local = local.replace(".", "")

    return f"{local}@{domain}"


def is_valid(email: str) -> bool:
    """Quick syntax check for an email address."""
    return _EMAIL_REGEX.match(email.strip().lower()) is not None


def validate_email(
    email: str,
    *,
    check_mx: bool = False,
    extra_disposable: list[str] | None = None,
) -> EmailResult:
    """Validate an email address with optional MX record lookup.

    Args:
        email: The email address to validate.
        check_mx: If True, attempt an MX DNS lookup for the domain.
        extra_disposable: Additional disposable domains to check against,
            merged with the built-in list for this call only.

    Returns:
        An EmailResult with validation details.
    """
    normalized = normalize(email)

    # Syntax check uses the raw lowered/stripped form (before normalization
    # removes dots/plus tags) to ensure the original address is well-formed.
    raw = email.strip().lower()
    if not _EMAIL_REGEX.match(raw):
        return EmailResult(
            valid=False,
            normalized=normalized,
            domain="",
            error="Invalid email syntax",
        )

    domain = normalized.rsplit("@", 1)[1]

    disposable_set: set[str] = DISPOSABLE_DOMAINS
    if extra_disposable:
        disposable_set = DISPOSABLE_DOMAINS | {d.lower().strip() for d in extra_disposable}

    disposable = domain in disposable_set

    if check_mx:
        try:
            try:
                import dns.resolver  # type: ignore[import-untyped]

                dns.resolver.resolve(domain, "MX")
            except ImportError:
                socket.getaddrinfo(domain, None)
        except Exception:
            return EmailResult(
                valid=False,
                normalized=normalized,
                domain=domain,
                error=f"MX lookup failed for domain: {domain}",
                is_disposable=disposable,
            )

    return EmailResult(
        valid=True,
        normalized=normalized,
        domain=domain,
        is_disposable=disposable,
    )


def validate_many(
    emails: list[str],
    *,
    check_mx: bool = False,
    concurrent: bool = True,
    extra_disposable: list[str] | None = None,
) -> list[EmailResult]:
    """Validate multiple email addresses.

    Args:
        emails: List of email addresses to validate.
        check_mx: If True, perform MX lookups.
        concurrent: If True and check_mx is True, use a thread pool for
            parallel MX lookups. Defaults to True.
        extra_disposable: Additional disposable domains to check against.

    Returns:
        A list of EmailResult objects, one per input email.
    """
    if check_mx and concurrent:
        with _futures.ThreadPoolExecutor() as executor:
            results = list(
                executor.map(
                    lambda e: validate_email(
                        e, check_mx=True, extra_disposable=extra_disposable
                    ),
                    emails,
                )
            )
        return results

    return [
        validate_email(email, check_mx=check_mx, extra_disposable=extra_disposable)
        for email in emails
    ]
