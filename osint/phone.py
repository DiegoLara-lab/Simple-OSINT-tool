import os
import httpx
import phonenumbers
from phonenumbers import carrier, geocoder, timezone, PhoneNumberType

LINE_TYPES = {
    PhoneNumberType.MOBILE: "mobile",
    PhoneNumberType.FIXED_LINE: "landline",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "landline or mobile",
    PhoneNumberType.VOIP: "voip",
    PhoneNumberType.TOLL_FREE: "toll free",
    PhoneNumberType.PREMIUM_RATE: "premium rate",
    PhoneNumberType.SHARED_COST: "shared cost",
    PhoneNumberType.PERSONAL_NUMBER: "personal number",
    PhoneNumberType.PAGER: "pager",
    PhoneNumberType.UAN: "universal access number",
    PhoneNumberType.VOICEMAIL: "voicemail",
    PhoneNumberType.UNKNOWN: "unknown",
}


def analyze(raw: str, default_region: str | None = None) -> dict:
    """Parse and analyze a phone number offline.

    default_region: two-letter country code (e.g. "US") used when the
    number is typed without a +country prefix.
    """
    try:
        parsed = phonenumbers.parse(raw, default_region)
    except phonenumbers.NumberParseException as e:
        return {"input": raw, "valid": False, "error": str(e)}

    return {
        "input": raw,
        "valid": phonenumbers.is_valid_number(parsed),
        "possible": phonenumbers.is_possible_number(parsed),
        "e164": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164),
        "international": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
        "national": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL),
        "country_code": parsed.country_code,
        "region": phonenumbers.region_code_for_number(parsed),
        "location": geocoder.description_for_number(parsed, "en") or "unknown",
        "original_carrier": carrier.name_for_number(parsed, "en") or "unknown",
        "timezones": list(timezone.time_zones_for_number(parsed)),
        "line_type_estimate": LINE_TYPES.get(phonenumbers.number_type(parsed), "unknown"),
    }


def twilio_lookup(e164: str) -> dict:
    """Optional paid lookup for current carrier and line type.
    Requires TWILIO_SID and TWILIO_TOKEN in your .env file."""
    sid, token = os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN")
    if not sid or not token:
        return {"error": "Twilio credentials not set"}

    url = f"https://lookups.twilio.com/v2/PhoneNumbers/{e164}"
    try:
        r = httpx.get(url, params={"Fields": "line_type_intelligence"},
                      auth=(sid, token), timeout=10)
        r.raise_for_status()
        data = r.json()
    except httpx.HTTPError as e:
        return {"error": str(e)}

    lti = data.get("line_type_intelligence") or {}
    return {
        "valid": data.get("valid"),
        "line_type": lti.get("type"),
        "current_carrier": lti.get("carrier_name"),
    }