import hashlib
import os
import re

import dns.resolver
import httpx

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")

FREE_PROVIDERS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com",
    "proton.me", "protonmail.com", "aol.com", "live.com", "msn.com",
    "gmx.com", "zoho.com",
}

DISPOSABLE = {
    "mailinator.com", "10minutemail.com", "guerrillamail.com", "tempmail.com",
    "yopmail.com", "trashmail.com", "sharklasers.com", "getnada.com",
    "throwawaymail.com", "maildrop.cc",
}

MX_PROVIDERS = {
    "google.com": "Google (Gmail / Workspace)",
    "googlemail.com": "Google (Gmail / Workspace)",
    "outlook.com": "Microsoft 365 / Outlook",
    "protection.outlook.com": "Microsoft 365",
    "pphosted.com": "Proofpoint (security gateway)",
    "mimecast.com": "Mimecast (security gateway)",
    "zoho.": "Zoho Mail",
    "protonmail.ch": "Proton Mail",
    "yahoodns.net": "Yahoo Mail",
    "icloud.com": "Apple iCloud Mail",
}


def _resolver() -> dns.resolver.Resolver:
    r = dns.resolver.Resolver()
    r.lifetime = 5
    return r


def _query(name: str, rtype: str) -> list[str]:
    try:
        answers = _resolver().resolve(name, rtype)
        return [a.to_text().strip('"') for a in answers]
    except Exception:
        return []


def _guess_provider(mx_hosts: list[str]) -> str:
    for host in mx_hosts:
        for needle, label in MX_PROVIDERS.items():
            if needle in host.lower():
                return label
    return "unknown / self-hosted" if mx_hosts else "none"


def analyze(raw: str) -> dict:
    """Validate an email and gather free DNS-based intelligence."""
    email = raw.strip().lower()
    if not EMAIL_RE.match(email):
        return {"input": raw, "valid_format": False,
                "error": "Not a valid email format"}

    local, domain = email.split("@")
    mx = [m.split()[-1].rstrip(".") for m in _query(domain, "MX")]
    txt = _query(domain, "TXT")
    dmarc = _query(f"_dmarc.{domain}", "TXT")

    return {
        "input": raw,
        "email": email,
        "valid_format": True,
        "username_part": local,
        "domain": domain,
        "domain_type": ("free provider" if domain in FREE_PROVIDERS
                        else "custom/company domain"),
        "disposable": domain in DISPOSABLE,
        "mx_records": mx or "none (cannot receive mail)",
        "mail_provider": _guess_provider(mx),
        "has_spf": any(t.startswith("v=spf1") for t in txt),
        "has_dmarc": any(t.startswith("v=DMARC1") for t in dmarc),
    }


def gravatar_exists(email: str) -> bool | str:
    """Free check: does this email have a public Gravatar avatar?"""
    h = hashlib.sha256(email.strip().lower().encode()).hexdigest()
    try:
        r = httpx.get(f"https://gravatar.com/avatar/{h}",
                      params={"d": "404"}, timeout=8, follow_redirects=True)
    except httpx.HTTPError as e:
        return f"error: {e}"
    return r.status_code == 200


def hibp_lookup(email: str) -> dict | str:
    """Breach lookup via Have I Been Pwned. Needs HIBP_API_KEY in .env."""
    key = os.getenv("HIBP_API_KEY")
    if not key:
        return "HIBP_API_KEY not set"
    try:
        r = httpx.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            params={"truncateResponse": "true"},
            headers={"hibp-api-key": key, "user-agent": "osint-tool"},
            timeout=10,
        )
    except httpx.HTTPError as e:
        return f"error: {e}"

    if r.status_code == 404:
        return {"breached": False, "breaches": []}
    if r.status_code == 200:
        names = [b["Name"] for b in r.json()]
        return {"breached": True, "count": len(names), "breaches": names}
    if r.status_code == 429:
        return "rate limited, try again shortly"
    return f"error: HTTP {r.status_code}"