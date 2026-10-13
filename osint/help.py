HELP_SECTIONS = {
    "Usage": [
        ("<number>", "Look up a phone number, e.g. +1 713 555 0123"),
        ("<email>", "Look up an email address, e.g. you@example.com"),
        ("links", "Show manual search links for the last phone number"),
        ("links <number>", "Show manual search links for a specific number"),
        ("?", "Show this help screen"),
        ("quit", "Exit interactive mode (also: exit, q)"),
    ],
    "Settings (interactive mode)": [
        ("region US", "Set the default country for numbers typed without a + prefix"),
        ("online on/off", "Turn online lookups on or off (Twilio, Gravatar, breach check)"),
        ("status", "Show current settings"),
    ],
    "Input formats": [
        ("+17135550123", "Phone, international format (no region needed)"),
        ("(713) 555-0123", "Phone, national format (needs a region, e.g. US)"),
        ("name@domain.com", "Email address (detected by the @ symbol)"),
    ],
    "Phone result fields": [
        ("valid", "Number matches a real numbering plan"),
        ("possible", "Length fits the country's rules (weaker check)"),
        ("e164", "Standardized international format"),
        ("original_carrier", "Carrier the number was first assigned to (may be outdated)"),
        ("line_type_estimate", "Guess based on the number range"),
        ("twilio", "Current carrier and line type (paid, needs API keys)"),
    ],
    "Email result fields": [
        ("valid_format", "Address is correctly formatted"),
        ("domain_type", "Free provider (Gmail, Yahoo...) or custom/company domain"),
        ("disposable", "Domain is a known temporary-email service"),
        ("mx_records", "Mail servers for the domain; none means it can't receive mail"),
        ("mail_provider", "Guessed from MX records (Google, Microsoft, etc.)"),
        ("has_spf / has_dmarc", "Whether the domain publishes email anti-spoofing records"),
        ("gravatar", "Public avatar exists for this email (online mode only)"),
        ("hibp", "Data breach exposure from Have I Been Pwned (online mode, needs API key)"),
    ],
    "Notes": [
        ("Authorization", "Only look up numbers and emails you have a legitimate reason to investigate"),
        ("API keys", "Stored in .env (TWILIO_SID, TWILIO_TOKEN, HIBP_API_KEY), never in code"),
    ],
}