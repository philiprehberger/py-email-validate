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
    "suggest_domain",
    "is_role_based",
    "DISPOSABLE_DOMAINS",
    "ROLE_PREFIXES",
    "COMMON_DOMAINS",
    "extract_emails",
    "EmailParts",
    "mask_email",
]

_EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)

_EXTRACT_REGEX = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
)

# RFC 5321 strict mode regex:
# - Local part: up to 64 characters, only printable ASCII (no spaces/specials
#   outside of quoted strings), dots allowed but not leading/trailing/consecutive
# - Domain: up to 255 characters, labels 1-63 chars, alphanumeric + hyphens
_RFC5321_LOCAL_RE = re.compile(
    r"^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~\-]"
    r"(?:[a-zA-Z0-9!#$%&'*+/=?^_`{|}~.\-]{0,62}[a-zA-Z0-9!#$%&'*+/=?^_`{|}~\-])?$"
)
_RFC5321_DOMAIN_RE = re.compile(
    r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
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

# Common role-based email prefixes (RFC 2142 and widely recognized roles)
ROLE_PREFIXES: frozenset[str] = frozenset({
    "abuse",
    "admin",
    "billing",
    "compliance",
    "devnull",
    "dns",
    "ftp",
    "hostmaster",
    "info",
    "inoc",
    "ispfeedback",
    "ispsupport",
    "list",
    "list-request",
    "maildaemon",
    "marketing",
    "noc",
    "no-reply",
    "noreply",
    "noc",
    "office",
    "phishing",
    "postmaster",
    "privacy",
    "registrar",
    "root",
    "sales",
    "security",
    "spam",
    "support",
    "sysadmin",
    "tech",
    "undisclosed-recipients",
    "unsubscribe",
    "usenet",
    "uucp",
    "webmaster",
    "www",
})

# Common domains used for typo suggestion
COMMON_DOMAINS: frozenset[str] = frozenset({
    "gmail.com",
    "googlemail.com",
    "yahoo.com",
    "yahoo.co.uk",
    "hotmail.com",
    "hotmail.co.uk",
    "outlook.com",
    "live.com",
    "aol.com",
    "icloud.com",
    "mail.com",
    "protonmail.com",
    "proton.me",
    "zoho.com",
    "yandex.com",
    "gmx.com",
    "gmx.de",
    "fastmail.com",
    "tutanota.com",
    "msn.com",
    "me.com",
    "mac.com",
    "comcast.net",
    "verizon.net",
    "att.net",
    "sbcglobal.net",
    "cox.net",
    "charter.net",
    "earthlink.net",
    "optonline.net",
})


def _levenshtein(a: str, b: str) -> int:
    """Compute the Levenshtein edit distance between two strings."""
    if len(a) < len(b):
        return _levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[len(b)]


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
    is_role_based: bool = field(default=False)
    suggested_domain: str = field(default="")


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


def is_role_based(email: str) -> bool:
    """Check whether an email uses a role-based local part.

    Role-based addresses like info@, admin@, or support@ are typically
    shared mailboxes rather than individual recipients.

    Args:
        email: The email address to check.

    Returns:
        True if the local part matches a known role prefix.
    """
    cleaned = email.strip().lower()
    if "@" not in cleaned:
        return False
    local = cleaned.rsplit("@", 1)[0]
    # Strip plus-addressing before checking
    if "+" in local:
        local = local.split("+", 1)[0]
    return local in ROLE_PREFIXES


def suggest_domain(domain: str) -> str:
    """Suggest a corrected domain for common typos.

    Compares the given domain against a built-in list of common email
    providers using edit distance. Returns the suggested domain if a
    close match is found, or an empty string if no suggestion applies.

    Args:
        domain: The domain part of an email address.

    Returns:
        A suggested domain string, or empty string if no suggestion.
    """
    domain = domain.strip().lower()
    if domain in COMMON_DOMAINS:
        return ""
    best_domain = ""
    best_dist = 3  # threshold: only suggest if distance <= 2
    for candidate in COMMON_DOMAINS:
        dist = _levenshtein(domain, candidate)
        if dist < best_dist:
            best_dist = dist
            best_domain = candidate
    return best_domain


def _validate_rfc5321_strict(local: str, domain: str) -> str:
    """Validate local and domain parts against RFC 5321 rules.

    Returns an error message if invalid, or empty string if valid.
    """
    if len(local) > 64:
        return "Local part exceeds 64 characters (RFC 5321)"
    if len(domain) > 255:
        return "Domain exceeds 255 characters (RFC 5321)"
    if ".." in local:
        return "Consecutive dots in local part (RFC 5321)"
    if local.startswith(".") or local.endswith("."):
        return "Local part starts or ends with a dot (RFC 5321)"
    if not _RFC5321_LOCAL_RE.match(local):
        return "Invalid characters in local part (RFC 5321)"
    if not _RFC5321_DOMAIN_RE.match(domain):
        return "Invalid domain format (RFC 5321)"
    for label in domain.split("."):
        if len(label) > 63:
            return "Domain label exceeds 63 characters (RFC 5321)"
    return ""


def validate_email(
    email: str,
    *,
    check_mx: bool = False,
    extra_disposable: list[str] | None = None,
    strict: bool = False,
) -> EmailResult:
    """Validate an email address with optional MX record lookup.

    Args:
        email: The email address to validate.
        check_mx: If True, attempt an MX DNS lookup for the domain.
        extra_disposable: Additional disposable domains to check against,
            merged with the built-in list for this call only.
        strict: If True, enforce RFC 5321 strict validation rules
            including local part length, domain label length, and
            character restrictions.

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
    raw_local = raw.rsplit("@", 1)[0]

    # RFC 5321 strict mode
    if strict:
        strict_error = _validate_rfc5321_strict(raw_local, domain)
        if strict_error:
            return EmailResult(
                valid=False,
                normalized=normalized,
                domain=domain,
                error=strict_error,
            )

    disposable_set: set[str] = DISPOSABLE_DOMAINS
    if extra_disposable:
        disposable_set = DISPOSABLE_DOMAINS | {d.lower().strip() for d in extra_disposable}

    disposable = domain in disposable_set
    role = is_role_based(raw)
    suggestion = suggest_domain(domain)

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
                is_role_based=role,
                suggested_domain=suggestion,
            )

    return EmailResult(
        valid=True,
        normalized=normalized,
        domain=domain,
        is_disposable=disposable,
        is_role_based=role,
        suggested_domain=suggestion,
    )


def validate_many(
    emails: list[str],
    *,
    check_mx: bool = False,
    concurrent: bool = True,
    extra_disposable: list[str] | None = None,
    strict: bool = False,
) -> list[EmailResult]:
    """Validate multiple email addresses.

    Args:
        emails: List of email addresses to validate.
        check_mx: If True, perform MX lookups.
        concurrent: If True and check_mx is True, use a thread pool for
            parallel MX lookups. Defaults to True.
        extra_disposable: Additional disposable domains to check against.
        strict: If True, enforce RFC 5321 strict validation rules.

    Returns:
        A list of EmailResult objects, one per input email.
    """
    if check_mx and concurrent:
        with _futures.ThreadPoolExecutor() as executor:
            results = list(
                executor.map(
                    lambda e: validate_email(
                        e,
                        check_mx=True,
                        extra_disposable=extra_disposable,
                        strict=strict,
                    ),
                    emails,
                )
            )
        return results

    return [
        validate_email(
            email,
            check_mx=check_mx,
            extra_disposable=extra_disposable,
            strict=strict,
        )
        for email in emails
    ]


@dataclass
class EmailParts:
    """Structured parts of an email address."""

    local: str
    domain: str
    tld: str
    normalized: str


def extract_emails(text: str) -> list[str]:
    """Extract all valid email addresses from a block of text.

    Finds email-like patterns and returns only those that pass syntax
    validation.  Duplicates are removed, preserving first-occurrence order.

    Args:
        text: The text to search for email addresses.

    Returns:
        A list of unique, valid email addresses found in the text.
    """
    candidates = _EXTRACT_REGEX.findall(text)
    seen: set[str] = set()
    results: list[str] = []
    for candidate in candidates:
        lower = candidate.strip().lower()
        if lower not in seen and is_valid(lower):
            seen.add(lower)
            results.append(lower)
    return results


def email_parts(email: str) -> EmailParts:
    """Split an email address into structured parts.

    Args:
        email: The email address to parse.

    Returns:
        An EmailParts dataclass with local, domain, tld, and normalized fields.

    Raises:
        ValueError: If the email has no '@' separator.
    """
    cleaned = email.strip().lower()
    if "@" not in cleaned:
        raise ValueError(f"Invalid email address: {email!r}")
    local, domain = cleaned.rsplit("@", 1)
    tld = domain.rsplit(".", 1)[-1] if "." in domain else ""
    return EmailParts(
        local=local,
        domain=domain,
        tld=tld,
        normalized=normalize(email),
    )


def mask_email(email: str, mask_char: str = "*", visible: int = 1) -> str:
    """Mask the local part of an email for privacy display.

    Args:
        email: The email address to mask.
        mask_char: Character used for masking. Defaults to ``"*"``.
        visible: Number of characters to keep visible at the start and end
            of the local part. Defaults to 1.

    Returns:
        The masked email string (e.g. ``"j***n@example.com"``).
    """
    cleaned = email.strip().lower()
    if "@" not in cleaned:
        return cleaned
    local, domain = cleaned.rsplit("@", 1)
    if len(local) <= visible * 2:
        masked_local = local[0] + mask_char * (len(local) - 1)
    else:
        masked_local = local[:visible] + mask_char * 3 + local[-visible:]
    return f"{masked_local}@{domain}"
