import yaml
import pandas as pd
import logging
import logging.config
import smtplib
import ssl
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from pretty_html_table import build_table
from tabulate import tabulate
from random import randint

from packages.db_connect import get_data

PRIVATE_YAML = Path("/home/cuddebtj/Documents/Python/mom_weekly_rankings_email/mom_weekly_rankings_email/assets/private.yaml")
with open(PRIVATE_YAML) as file:
    private = yaml.load(file, Loader=yaml.SafeLoader)

LOG_CONFIG_PATH = Path("/home/cuddebtj/Documents/Python/mom_weekly_rankings_email/mom_weekly_rankings_email/assets/logger_config.yaml")
with open(LOG_CONFIG_PATH, 'rb') as config:
    log_config = yaml.safe_load(config.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)

try:
    JMU_LOGO_PATH = Path("/home/cuddebtj/Documents/Python/mom_weekly_rankings_email/mom_weekly_rankings_email/assets/JMU-Logo-RGB-vert-purple.png")
    SALUTAIONS = Path("/home/cuddebtj/Documents/Python/mom_weekly_rankings_email/mom_weekly_rankings_email/assets/salutations.yaml")

    with open(SALUTAIONS) as file:
        salutation_list = yaml.load(file, Loader=yaml.SafeLoader)

except Exception as e:
    logger.critical(f'Error: {e}', exc_info=True)


def send_weekly_rankings(week, plain_body, html_body):

    _to = ';'.join(private["email_list"])
    _from = private["mom_email"]
    _to = 'cuddebtj@gmail.com'

    try:
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(private["host"], private["port"], context=context) as server:
            server.login(_from, private["gmail_app_pass"])

            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"MoM FFBL Weekly Rankings: Week {week}"
            msg["From"] = f"{_from}"
            msg["To"] = f"{_to}"
            jmu_logo = MIMEImage(open(JMU_LOGO_PATH, 'r').read())
            jmu_logo.add_header('Content-ID', '<jmu_logo>')
            msg.attach(jmu_logo)
            msg.attach(MIMEText(plain_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            server.sendmail(_from, _to, msg.as_string())

    except Exception as e:
        logger.critical(f'Error: {e}', exc_info=True)

def main():

    df = get_data()

    try:
        cur_week = df["Week"].max()

        rankings = df[
            [
                "Team",
                "Manager",
                "Cur. Wk Rk",
                "Prev. Wk Rk",
                "2pt Ttl",
                "2pt Ttl Rk",
                "Ttl Pts Win",
                "Ttl Pts Win Rk",
                "Win Ttl",
                "Loss Ttl",
                "W/L Rk",
                "Ttl Pts",
                "Ttl Pts Rk",
                "Avg Pts",
                "Ttl Opp Pts",
                "Avg Opp Pts",
                "Wk W/L",
                "Wk Pts W/L",
                "Wk Pts",
                "Wk Pts Rk",
                "Opp Team",
                "Opp Manager",
                "Opp Wk Pts",
                "Opp Wk Pts Rk",
            ]
        ]

    except Exception as e:
        logger.error('Data error', exc_info=True)

    try:
        html_rankings = build_table(
            rankings,
            "grey_dark",
            font_family="Arial",
            text_align="center",
            width_dict=[
                "200px", # Team
                "100px", # Manager
                "40px", # Cur. Wk Rk
                "40px", # Prev. Wk Rk
                "40px", # 2pt Ttl
                "40px", # 2pt Ttl Rk
                "40px", # Ttl Pts Win
                "40px", # Ttl Pts Win Rk
                "40px", # Win Ttl
                "40px", # Loss Ttl
                "40px", # W/L Rk
                "80px", # Ttl Pts
                "40px", # Ttl Pts Rk
                "60px", # Avg Pts
                "80px", # Ttl Opp Pts
                "60px", # Avg Opp Pts
                "40px", # Wk W/L
                "40px", # Wk Pts W/L
                "60px", # Wk Pts
                "200px", # Opp Team
                "100px", # Opp Manager
                "60px", # Opp Wk Pts
                "40px", # Opp Wk Pts Rk
            ],
        )

    except Exception as e:
        logger.error('HTML table error', exc_info=True)

    try:
        salutation = salutation_list["salutations"][
            randint(0, len(salutation_list["salutations"])-1)
        ]

    except Exception as e:
        logger.error('Salutation error', exc_info=True)

    try:
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
            <img alt="JMU-Logo" width="306" height="198" style="border:none;" src="cid:jmu_logo" >
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

        plain_body = plain_body.format(
            table=tabulate(rankings, headers="firstrow", tablefmt="grid"), salutation=salutation
        )
        html_body = html_body.format(table=html_rankings, salutation=salutation)
    
    except Exception as e:
        logger.error('Email body build error', exc_info=True)

    send_weekly_rankings(cur_week, plain_body, html_body)

if __name__ == '__main__':
    main()
    print("Done")