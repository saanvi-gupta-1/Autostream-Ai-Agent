import re
import json
import datetime
from pathlib import Path

LOG_PATH = Path(__file__).parent / "leads_log.json"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"

# Common disposable/invalid domains to reject
BLOCKED_DOMAINS = {
    "example.com", "test.com", "invalid.com", "fake.com",
    "mailinator.com", "tempmail.com", "throwaway.email",
    "guerrillamail.com", "yopmail.com", "sharklasers.com",
}

# Common valid email providers for quick-pass
KNOWN_PROVIDERS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "protonmail.com", "icloud.com", "aol.com", "zoho.com",
    "live.com", "msn.com", "mail.com", "yandex.com",
    "pm.me", "fastmail.com", "tutanota.com",
}


def validate_email(email: str) -> bool:
    """Validate email with format check, domain validation, and blocklist."""
    if not email or not isinstance(email, str):
        return False

    email = email.strip().lower()

    # Basic regex check
    if not re.match(EMAIL_REGEX, email):
        return False

    # Split into local + domain
    parts = email.split("@")
    if len(parts) != 2:
        return False

    local, domain = parts

    # Local part checks
    if len(local) < 1 or len(local) > 64:
        return False
    if local.startswith(".") or local.endswith("."):
        return False
    if ".." in local:
        return False

    # Domain checks
    if len(domain) < 4:  # minimum: a.co
        return False
    if domain in BLOCKED_DOMAINS:
        return False

    # Domain must have at least one dot and valid TLD
    domain_parts = domain.split(".")
    if len(domain_parts) < 2:
        return False

    tld = domain_parts[-1]
    if len(tld) < 2 or len(tld) > 10:
        return False

    # Each domain label must be alphanumeric (with hyphens)
    for part in domain_parts:
        if not part or len(part) > 63:
            return False
        if not re.match(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]*[a-zA-Z0-9])?$", part):
            return False

    return True


def validate_name(name: str) -> bool:
    """Validate that a name contains only letters, spaces, hyphens, and apostrophes."""
    if not name or not isinstance(name, str):
        return False

    name = name.strip()

    # Must be 2-60 characters
    if len(name) < 2 or len(name) > 60:
        return False

    # Only letters, spaces, hyphens, apostrophes, and periods (for initials)
    if not re.match(r"^[a-zA-Z][a-zA-Z\s'\-\.]*[a-zA-Z]$", name):
        return False

    # Must contain at least 2 letters
    letter_count = sum(1 for c in name if c.isalpha())
    if letter_count < 2:
        return False

    # Reject if it looks like an email, URL, or number
    if "@" in name or "." in name.split()[-1] or any(c.isdigit() for c in name):
        return False

    return True


def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    print(f"Lead captured successfully: {name}, {email}, {platform}")

    if not all([name.strip(), email.strip(), platform.strip()]):
        return {"success": False, "error": "All fields (name, email, platform) are required."}

    if not validate_email(email):
        return {"success": False, "error": "Invalid email format."}

    lead_id = f"LEAD-{abs(hash(email)) % 100000:05d}"
    timestamp = datetime.datetime.now().isoformat()

    lead_record = {
        "lead_id": lead_id,
        "name": name.strip(),
        "email": email.strip().lower(),
        "platform": platform.strip(),
        "source": "AutoStream Social Agent",
        "plan_interest": "Pro Plan",
        "captured_at": timestamp,
    }

    leads = []
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            try:
                leads = json.load(f)
            except json.JSONDecodeError:
                leads = []

    leads.append(lead_record)

    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2)

    return {
        "success": True,
        "lead_id": lead_id,
        "name": name.strip(),
        "email": email.strip().lower(),
        "platform": platform.strip(),
        "timestamp": timestamp,
    }
