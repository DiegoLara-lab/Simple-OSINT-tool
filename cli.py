import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from osint import phone
from osint import emailcheck
from osint.helpview import show_help
from osint.links import build_links

load_dotenv()
app = typer.Typer(add_completion=False)
console = Console()

HELP_TRIGGERS = {"?", "help", "-h", "--help"}


def print_table(title: str, data: dict) -> None:
    table = Table(title=title)
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    for key, value in data.items():
        table.add_row(key, str(value))
    console.print(table)


def run_lookup(number: str, region: str | None, online: bool) -> dict | None:
    result = phone.analyze(number, region)

    if "error" in result:
        console.print(f"[red]Could not parse number:[/red] {result['error']}")
        console.print("Type [cyan]?[/cyan] for help.")
        return None

    if online and result["valid"]:
        result["twilio"] = phone.twilio_lookup(result["e164"])

    print_table(f"Results for {number}", result)
    return result


def run_email(address: str, online: bool) -> None:
    result = emailcheck.analyze(address)
    if "error" in result:
        console.print(f"[red]{result['error']}[/red]")
        return

    if online:
        result["gravatar"] = emailcheck.gravatar_exists(result["email"])
        result["hibp"] = emailcheck.hibp_lookup(result["email"])

    print_table(f"Results for {address}", result)
    if not online:
        msg = "Type [cyan]online on[/cyan] to add Gravatar and breach checks."
        console.print(msg)


def show_links(info: dict) -> None:
    console.print("[bold]Manual lookup links[/bold] (open in your browser):")
    for label, url in build_links(info).items():
        console.print(f"[cyan]{label}[/cyan]")
        console.print(f"  {url}", soft_wrap=True)


def interactive(region: str | None, online: bool) -> None:
    console.print("[bold]OSINT tool[/bold]. Type [cyan]?[/cyan] for help.")
    last: dict | None = None
    while True:
        try:
            line = console.input("[green]>[/green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        if not line:
            continue
        cmd = line.lower()

        if cmd in HELP_TRIGGERS:
            show_help(console)
        elif cmd in {"quit", "exit", "q"}:
            break
        elif cmd.startswith("region "):
            region = line.split(maxsplit=1)[1].upper()
            console.print(f"Default region set to [cyan]{region}[/cyan]")
        elif cmd.startswith("online "):
            online = cmd.endswith("on")
            state = "on" if online else "off"
            console.print(f"Online lookup: [cyan]{state}[/cyan]")
        elif cmd == "status":
            reg = region or "not set"
            onl = "on" if online else "off"
            console.print(f"Region: {reg} | Online lookup: {onl}")
        elif cmd == "links" or cmd.startswith("links "):
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                info = phone.analyze(parts[1], region)
                if "error" in info or not info["valid"]:
                    console.print("[red]That number isn't valid.[/red]")
                    continue
                last = info
            if last is None:
                msg = "Look up a number first, or type [cyan]links <number>[/cyan]."
                console.print(msg)
            else:
                show_links(last)
        else:
            if "@" in line:
                run_email(line, online)
                continue
            result = run_lookup(line, region, online)
            if result and result["valid"]:
                last = result
                msg = "Type [cyan]links[/cyan] for manual search links."
                console.print(msg)


@app.command()
def main(
    number: str = typer.Argument(None, help="Phone number or email, or ? for help"),
    region: str = typer.Option(None, help="Default country, e.g. US"),
    online: bool = typer.Option(False, help="Also run online lookups"),
    links: bool = typer.Option(False, help="Also print manual search links"),
):
    if number is None:
        interactive(region, online)
    elif number.strip().lower() in HELP_TRIGGERS:
        show_help(console)
    elif "@" in number:
        run_email(number, online)
    else:
        result = run_lookup(number, region, online)
        if result is None:
            raise typer.Exit(1)
        if links and result["valid"]:
            show_links(result)


if __name__ == "__main__":
    app()