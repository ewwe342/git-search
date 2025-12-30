import requests
import random
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, DataTable, Static
from textual.containers import Container
from textual.binding import Binding

class Snowfall(Static):
    def on_mount(self):
        self.set_interval(0.1, self.update_snow)
        self.snow_chars = ["❄", "❅", "❆", "·"]
        self.particles = []

    def update_snow(self):
        width = self.size.width
        if width > 0:
            if len(self.particles) < 50:
                self.particles.append([random.randint(0, width - 1), 0, random.choice(self.snow_chars)])
            
            canvas = [" "] * (width * self.size.height)
            new_particles = []
            for p in self.particles:
                p[1] += 1
                if p[1] < self.size.height:
                    idx = p[1] * width + p[0]
                    if idx < len(canvas):
                        canvas[idx] = p[2]
                    new_particles.append(p)
            self.particles = new_particles
            self.update("".join(canvas))

class GitSearchApp(App):
    TITLE = "Git Search 2026"
    CSS = """
    Screen { align: center middle; background: #06080a; }
    #search-container { width: 90%; height: 90%; border: double skyblue; padding: 1; background: #0d1117; }
    Snowfall { color: white; height: 100%; width: 100%; position: absolute; }
    DataTable { height: 1fr; margin-top: 1; border: round #30363d; }
    Input { border: tall #58a6ff; }
    """
    BINDINGS = [Binding("q", "quit", "Exit")]

    def compose(self) -> ComposeResult:
        yield Snowfall()
        with Container(id="search-container"):
            yield Header()
            yield Input(placeholder="Search repositories (e.g. 'fastapi stars:>5000')...")
            yield DataTable()
            yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.add_columns("Repository", "Stars", "Description")
        
        url = f"https://api.github.com/search/repositories?q={event.value}&sort=stars&order=desc"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                for repo in response.json().get("items", [])[:20]:
                    desc = repo["description"] or "No description"
                    table.add_row(
                        repo["full_name"],
                        f"⭐ {repo['stargazers_count']}",
                        (desc[:75] + "...") if len(desc) > 75 else desc
                    )
        except:
            pass

if __name__ == "__main__":
    GitSearchApp().run()