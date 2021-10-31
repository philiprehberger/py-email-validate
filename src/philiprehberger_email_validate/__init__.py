"""Email validation with syntax checking and normalization."""

from __future__ import annotations

import concurrent.futures
import re
import socket
from dataclasses import dataclass, field

__all__ = [
    "EmailResult",
    "normalize",
    "is_valid",
    "validate_email",
    "validate_many",
]

_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

DISPOSABLE_DOMAINS: set[str] = {
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
}


@dataclass
class EmailResult:
    """Result of an email validation check."""

    valid: bool
    normalized: str
    domain: str
    error: str = field(default="")
    is_disposable: bool = field(default=False)


def normalize(email: str) -> str:
    """Strip whitespace and lowercase an email address."""
    return email.strip().lower()


def is_valid(email: str) -> bool:
    """Quick syntax check for an email address."""
    return _EMAIL_REGEX.match(normalize(email)) is not None


def validate_email(email: str, *, check_mx: bool = False) -> EmailResult:
    """Validate an email address with optional MX record lookup.

    Args:
        email: The email address to validate.
        check_mx: If True, attempt an MX DNS lookup for the domain.

    Returns:
        An EmailResult with validation details.
    """
    normalized = normalize(email)

    if not _EMAIL_REGEX.match(normalized):
        return EmailResult(
            valid=False,
            normalized=normalized,
            domain="",
            error="Invalid email syntax",
        )

    domain = normalized.rsplit("@", 1)[1]
    disposable = domain in DISPOSABLE_DOMAINS

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
    emails: list[str], *, check_mx: bool = False
) -> list[EmailResult]:
    """Validate multiple email addresses.

    Args:
        emails: List of email addresses to validate.
        check_mx: If True, perform parallel MX lookups using a thread pool.

    Returns:
        A list of EmailResult objects, one per input email.
    """
    if check_mx:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(
                executor.map(
                    lambda e: validate_email(e, check_mx=True), emails
                )
            )
        return results

    return [validate_email(email, check_mx=False) for email in emails]
