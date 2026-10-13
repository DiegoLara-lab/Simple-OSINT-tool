from urllib.parse import quote_plus


def _formats(info: dict) -> list[str]:
    """Different ways people write the same number."""
    formats = [info["e164"], info["international"], info["national"]]
    digits = info["e164"].lstrip("+")
    if info["country_code"] == 1 and len(digits) == 11:
        d = digits[1:]
        formats.append(f"{d[:3]}-{d[3:6]}-{d[6:]}")
    seen, unique = set(), []
    for f in formats:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def build_links(info: dict) -> dict[str, str]:
    """Return {label: url} for manual lookups. Opened by a human in a browser."""
    formats = _formats(info)
    any_format = " OR ".join(f'"{f}"' for f in formats)

    def google(query: str) -> str:
        return "https://www.google.com/search?q=" + quote_plus(query)

    links = {
        "Search (all formats)": google(any_format),
        "Spam reports (800notes)": google(f'site:800notes.com ({any_format})'),
        "Spam reports (Who Called Me)": google(f'site:whocalledme.com ({any_format})'),
        "Scam mentions": google(f'({any_format}) scam OR spam OR fraud'),
    }

    # US numbers only: direct page. Verify the URL pattern on the site.
    digits = info["e164"].lstrip("+")
    if info["country_code"] == 1 and len(digits) == 11:
        d = digits[1:]
        links["USPhoneBook (US only)"] = f"https://www.usphonebook.com/{d[:3]}-{d[3:6]}-{d[6:]}"

    return links