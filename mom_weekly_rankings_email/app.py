import yaml
import pandas as pd
from pathlib import Path
from pretty_html_table import build_table
from tabulate import tabulate
from random import randint


from packages.db_connect import get_data
from packages.send_message import send_weekly_rankings

PRIVATE = list(Path().cwd().glob("**/private.yaml"))[0]
SALUTAIONS = list(Path().cwd().glob("**/salutations.yaml"))[0]
with open(SALUTAIONS) as file:
    salutation_list = yaml.load(file, Loader=yaml.SafeLoader)

df = get_data(PRIVATE)

cur_week = df["Week"].max()

rankings = df[["Team", "Manager", "Cur. Wk Rk", "Prev. Wk Rk", "2pt Ttl", "Ttl Pts Win", "Ttl Pts Win Rk", "Win Ttl", "Loss Ttl", "W/L Rk", "Ttl Pts", "Ttl Pts Rk", "Avg Pts", "Ttl Opp Pts", "Avg Opp Pts", "Wk W/L", "Wk Pts", "Opp Team", "Opp Manager", "Opp Wk Pts", "Opp Wk Pts Rk"]]

html_rankings = build_table(rankings, "grey_dark", font_family="Arial", text_align="center", width_dict=["200px", "100px" , "40px", "40px", "40px", "40px", "40px", "40px", "40px", "40px", "80px", "40px", "60px", "80px", "60px", "40px", "60px", "200px", "100px", "60px", "40px"])

salutation = salutation_list["salutations"][randint(0, len(salutation_list["salutations"]))]

plain_body = """\
    Here is the currently weekly rankings!
    Keep an eye out for more emails/add this email to your safe senders so it doesn't got to spam.

    {table}

    {salutation}

    Column Info:
        - Ttl Pts Win = Total wins against league median
        - Ttl Pts Rk = Rank of total points scored this season, used as tie breaker
        - Avg Pts = Average points scored per week to this point
        - Ttl Opp Pts = Total points against
        - Avg Opp Pts = Average points against
        - Wk Pts W/L = Win or Loss against league median current week
"""

html_body = """\
<html>
  <body>
    <h1>Here is the currently weekly rankings!</h1>
	<br>
    <h2>Keep an eye out for more emails/add this email to your safe senders so it doesn't got to spam.</h2>
	<br>
	{table}
    <br>
	<h2>{salutation}</h2>
    <br>
    <p>Column Info:</p>
    <ul>
        <li>Ttl Pts Win = Total wins against league median</li>
        <li>Ttl Pts Rk = Rank of total points scored this season, used as tie breaker</li>
        <li>Avg Pts = Average points scored per week to this point</li>
        <li>Avg Opp Pts = Average points against</li>
        <li>Wk Pts W/L = Win or Loss against league median current week</li>
    </ul>
  </body>
</html>
"""

plain_body = plain_body.format(table=tabulate(rankings, headers="firstrow", tablefmt="grid"), salutation=salutation)
html_body = html_body.format(table=html_rankings, salutation=salutation)

send_weekly_rankings(cur_week, plain_body, html_body)
