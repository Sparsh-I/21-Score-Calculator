import reflex as rx
from dataclasses import dataclass, replace

JOKER_PTS = {0: 0, 1: 4, 2: 10}
ADJACENT_PTS = {0: 0, 1: 2, 2: 6, 3: 10}

def to_int(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        return 0

def bonus_for(p: Player) -> int:
    j = to_int(p.joker_count)
    l = to_int(p.adj_l_count)
    r = to_int(p.adj_r_count)

    marriages = min(j, l, r)
    j, l, r = j - marriages, l - marriages, r - marriages

    return (
        marriages * 10 
        + JOKER_PTS[min(j, 2)]
        + ADJACENT_PTS[min(l, 3)]
        + ADJACENT_PTS[min(r, 3)]
    )

@dataclass
class Player:
    name: str
    score: int = 0
    joker_count: str = ""
    adj_l_count: str = ""
    adj_r_count: str = ""
    bonus_points : int = 0


class State(rx.State):
    num_input: str = ""
    players: list[Player] = []

    @rx.event
    def set_num_input(self, value: str):
        self.num_input = value

    @rx.event
    def add_players(self):
        try:
            n = int(self.num_input)
        except ValueError:
            return
        n = max(0, min(n, 20))
        start = len(self.players)
        for i in range(n):
            self.players.append(Player(name=f"Player {start + i + 1}"))
        self.num_input = ""

    @rx.event
    def change_player_score(self, index: int, amount: int):
        self.players[index] = replace(
            self.players[index],
            score=self.players[index].score + amount
        )

    @rx.event
    def change_other_players_score(self, index: int, amount: int):
        for i in range(len(self.players)):
            if i != index:
                self.change_player_score(i, amount)

    
    @rx.event
    def chunga_munga(self, index: int):
        self.change_player_score(index, 10 * (len(self.players)-1))
        self.change_other_players_score(index, -10)

    @rx.event
    def set_field(self, index: int, field: str, value: str):
        self.players[index] = replace(self.players[index], **{field: value})

    @rx.event
    def calculate_all_bonuses(self):
        self.players = [
            replace(p, bonus_points=bonus_for(p)) for p in self.players
        ]

    @rx.event
    def clear_players(self):
        self.players = []

def player_card(player: Player, index: int):
    """The standard player card will look like this"""
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(player.name, weight="bold", size="4"),
                rx.text("Payout", weight="light", size="1", color_scheme="gray"),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            rx.button("-", color_scheme="ruby",
                      on_click=State.change_player_score(index, -1)),
            rx.heading(player.score, size="6", min_width="2em", text_align="center"),
            rx.button("+", color_scheme="grass",
                      on_click=State.change_player_score(index, 1)),
            rx.spacer(),
            rx.button("Chunga Munga", color_scheme="sky",
                      on_click=State.chunga_munga(index)),
            rx.spacer(),
            rx.vstack(
                rx.text("Bonus points", weight="bold", size="4"),
                rx.text(player.bonus_points, weight="light", size="4", color_scheme="gray"),
                spacing="2",
                align="start",
            ),
            rx.spacer(),
            rx.hstack(
                rx.vstack(
                    rx.text("# of Jokers"),
                    rx.input(
                        placeholder="How many jokers?",
                        type="number",
                        value=player.joker_count,
                        on_change=lambda v: State.set_field(index, "joker_count", v),
                    )
                ), 
                rx.vstack(
                    rx.text("# of Adjacent L"),
                    rx.input(
                        placeholder="L adjacent jokers?",
                        type="number",
                        value=player.adj_l_count,
                        on_change=lambda v: State.set_field(index, "adj_l_count", v),
                    )
                ),
                rx.vstack(
                    rx.text("# of Adjacent R"),
                    rx.input(
                        placeholder="R adjacent jokers?",
                        type="number",
                        value=player.adj_r_count,
                        on_change=lambda v: State.set_field(index, "adj_r_count", v),
                    )
                ),
            ),
            rx.spacer(),
            align="center",
            spacing="3",
            width="100%",
        ),
        width="100%",
    )

def index():
    return rx.vstack(
        rx.heading("21 Score Calculator"),
        rx.hstack(
            rx.input(
                placeholder="Input number of players",
                type="number",
                value=State.num_input,
                on_change=State.set_num_input,
            ),
            rx.button(
                "Add Players",
                color_scheme="grass",
                on_click=State.add_players,
            ),
            rx.button(
                "Clear Players",
                color_scheme="ruby",
                on_click=State.clear_players,
            ),
            spacing="3"
        ),
        rx.foreach(State.players, player_card),
        rx.button(
            "Calculate",
            color_scheme="iris",
            on_click=State.calculate_all_bonuses,
        ),
        spacing="4",
        padding="2em"
    )

app = rx.App()
app.add_page(index)