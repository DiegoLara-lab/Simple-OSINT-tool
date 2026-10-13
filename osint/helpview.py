from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from osint.help import HELP_SECTIONS


def show_help(console: Console) -> None:
    for title, rows in HELP_SECTIONS.items():
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="cyan", no_wrap=True)
        table.add_column()
        for key, desc in rows:
            table.add_row(key, desc)
        console.print(Panel(table, title=title, title_align="left"))