import reflex as rx
from dataclasses import dataclass, replace

def to_int(text: str) -> int:
    try:
        return int(text)
    except ValueError:
        return 0

JOKER_PTS = {0: 0, 1: 4, 2: 10}
ADJACENT_PTS = {0: 0, 1: 2, 2: 6, 3: 10}

@dataclass
class Player:
    name: str
    payout: int = 0
    hand_val: str = ""
    joker_count: str = ""
    adj_l_count: str = ""
    adj_r_count: str = ""
    london_count: str = ""
    bonus_points : int = 0

def bonus_for(p: Player) -> int:
    londons = to_int(p.london_count)

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
        + londons * 2
    )

class State(rx.State):
    num_input: str = ""
    players: list[Player] = []
    winner: int = -1

    @rx.event
    def select_winner(self, value: str):
        self.winner = to_int(value)

    @rx.event
    def set_num_input(self, value: str):
        self.num_input = value

    @rx.event
    def update_player_name(self, index: int, value: str):
        self.players[index] = replace(self.players[index], name=value)

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
    def change_player_payout(self, index: int, amount: int):
        self.players[index] = replace(
            self.players[index],
            payout=self.players[index].payout + amount
        )
    
    @rx.event
    def chunga_munga(self, index: int):
        n = len(self.players)
        self.players = [
            replace(p, payout=p.payout + (10 * (n-1) if i == index else -10))
            for i, p in enumerate(self.players)
        ]

    @rx.event
    def set_field(self, index: int, field: str, value: str):
        self.players[index] = replace(self.players[index], **{field: value})

    @rx.event
    def calculate_all_bonuses(self):
        self.players = [
            replace(p, bonus_points=bonus_for(p), joker_count="", adj_l_count="", adj_r_count="", london_count="")
            for p in self.players
        ]

    @rx.event
    def calculate_payouts(self):
        self.calculate_all_bonuses()

        if self.winner == -1 or len(self.players) < 2:
            return
        else:
            for i, p in enumerate(self.players):
                if i == self.winner:
                    for l in self.players:
                        p.payout += p.bonus_points + round(int(l.hand_val)/10) - l.bonus_points
                        l.payout -= p.bonus_points + round(int(l.hand_val)/10) - l.bonus_points
                else:
                    for j, l in enumerate(self.players):
                        if j != self.winner:
                            p.payout += p.bonus_points - l.bonus_points

        self.players = [replace(p, hand_val=0) for p in self.players]

    @rx.event
    def clear_players(self):
        self.players = []

def player_card(player: Player, index: int):
    """The standard player card will look like this"""
    return rx.card(
        rx.hstack(
            rx.input(placeholder="Player " + (index + 1).to(str) + "'s Name", type="text",
                     value=player.name, on_change=lambda v:State.update_player_name(index, v),
                     variant="soft", background="transparent", box_shadow="none", font_weight="bold", font_size="1.4em",),
            rx.spacer(),
            rx.button("-", color_scheme="ruby",
                      on_click=State.change_player_payout(index, -1)),
            rx.heading(player.payout, size="6", min_width="2em", text_align="center"),
            rx.button("+", color_scheme="grass",
                      on_click=State.change_player_payout(index, 1)),
            rx.spacer(),
            rx.button("Chunga Munga", color_scheme="sky",
                      on_click=State.chunga_munga(index)),
            rx.spacer(),
            rx.vstack(
                rx.text("Winner?"),
                rx.radio_group.item(value=index.to(str)),
            ),
            rx.spacer(),
            rx.vstack(
                rx.text("Hand Value"),
                rx.input(placeholder="Hand value", type="number",
                    value=player.hand_val, on_change=lambda v: State.set_field(index, "hand_val", v),
                ),
                width="6em"
            ),
            rx.spacer(),
            rx.vstack(
                rx.text("Bonus", weight="bold", size="4"),
                rx.text(player.bonus_points, weight="light", size="4", color_scheme="gray"),
                spacing="2",
                align="start",
            ),
            rx.spacer(),
            rx.hstack(
                rx.vstack(
                    rx.text("# of J"),
                    rx.input(placeholder="Jokers?", type="number",
                             value=player.joker_count, on_change=lambda v: State.set_field(index, "joker_count", v),
                    ),
                    width="5em"
                ), 
                rx.vstack(
                    rx.text("# of L"),
                    rx.input(placeholder="L jokers?", type="number",
                             value=player.adj_l_count, on_change=lambda v: State.set_field(index, "adj_l_count", v),
                    ),
                    width="5em"
                ),
                rx.vstack(
                    rx.text("# of R"),
                    rx.input(placeholder="R jokers?", type="number",
                             value=player.adj_r_count, on_change=lambda v: State.set_field(index, "adj_r_count", v),
                    ),
                    width="5em"
                ),
            ),
            rx.spacer(),
            rx.vstack(
                rx.text("Londons"),
                rx.input(placeholder="Londons?", type="number",
                            value=player.london_count, on_change=lambda v: State.set_field(index, "london_count", v),
                ),
                width="5em"
            ), 
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
            rx.input(placeholder="Input number of players", type="number",
                     value=State.num_input, on_change=State.set_num_input,
                     width="175px"
                    ),
            rx.button("Add Players", color_scheme="grass", on_click=State.add_players),
            rx.button("Clear Players", color_scheme="ruby", on_click=State.clear_players),
            spacing="3"
        ),
        rx.radio_group.root(
            rx.vstack(
                rx.foreach(State.players, player_card),
            ),
            value=State.winner.to(str),
            on_change=State.select_winner,
            width="100%"
        ),
        rx.cond(State.players.length() > 0,
                rx.button("Calculate", color_scheme="iris", on_click=State.calculate_payouts)),
        spacing="4",
        padding="2em"
    )

app = rx.App()
app.add_page(index)