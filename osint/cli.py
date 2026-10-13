import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from osint import phone
from osint.helpview import show_help
from osint.links import build_links

load_dotenv()
app = typer.Typer(add_completion=False)
console = Console()

HELP_TRIGGERS = {"?", "help", "-h", "--help"}


def run_lookup(number: str, region: str | None, online: bool) -> dict | None:
    result = phone.analyze(number, region)

    if "error" in result:
        console.print(f"[red]Could not parse number:[/red] {result['error']}")
        console.print("Type [cyan]?[/cyan] for help.")
        return None

    if online and result["valid"]:
        result["twilio"] = phone.twilio_lookup(result["e164"])

    table = Table(title=f"Results for {number}")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    for key, value in result.items():
        table.add_row(key, str(value))
    console.print(table)
    return result


def show_links(info: dict) -> None:
    console.print("[bold]Manual lookup links[/bold] (open in your browser):")
    for label, url in build_links(info).items():
        console.print(f"[cyan]{label}[/cyan]")
        console.print(f"  {url}", soft_wrap=True)


def interactive(region: str | None, online: bool) -> None:
    console.print("[bold]Phone OSINT tool[/bold]. Type [cyan]?[/cyan] for help.")
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
            console.print(f"Online lookup: [cyan]{'on' if online else 'off'}[/cyan]")
        elif cmd == "status":
            console.print(f"Region: {region or 'not set'} | Online lookup: {'on' if online else 'off'}")
        elif cmd == "links" or cmd.startswith("links "):
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                info = phone.analyze(parts[1], region)
                if "error" in info or not info["valid"]:
                    console.print("[red]That number isn't valid.[/red]")
                    continue
                last = info
            if last is None:
                console.print("Look up a number first, or type [cyan]links <number>[/cyan].")
            else:
                show_links(last)
        else:
            result = run_lookup(line, region, online)
            if result and result["valid"]:
                last = result
                console.print("Type [cyan]links[/cyan] for manual search links.")


@app.command()
def main(
    number: str = typer.Argument(None, help="Phone number, or ? for help"),
    region: str = typer.Option(None, help="Default country, e.g. US"),
    online: bool = typer.Option(False, help="Also run the Twilio lookup"),
    links: bool = typer.Option(False, help="Also print manual search links"),
):
    if number is None:
        interactive(region, online)
    elif number.strip().lower() in HELP_TRIGGERS:
        show_help(console)
    else:
        result = run_lookup(number, region, online)
        if result is None:
            raise typer.Exit(1)
        if links and result["valid"]:
            show_links(result)


if __name__ == "__main__":
    app()
