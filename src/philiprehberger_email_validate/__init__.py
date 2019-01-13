"""Email validation with syntax checking and normalization."""

from __future__ import annotations

import re
import socket
from dataclasses import dataclass, field

__all__ = ["EmailResult", "normalize", "is_valid", "validate_email"]

_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)


@dataclass
class EmailResult:
    """Result of an email validation check."""

    valid: bool
    normalized: str
    domain: str
    error: str = field(default="")


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
            )

    return EmailResult(valid=True, normalized=normalized, domain=domain)
