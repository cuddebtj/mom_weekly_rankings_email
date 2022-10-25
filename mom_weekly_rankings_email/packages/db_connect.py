import psycopg2
import yaml
import pandas as pd
import logging
from io import StringIO
from pathlib import Path

logger = logging.getLogger(__name__)

def get_data():
    query = """
    SELECT "Week"
    , "Team"
    , "Manager"
    , "Cur. Wk Rk"
    , "Prev. Wk Rk"
    , "2pt Ttl"
    , "2pt Ttl Rk"
    , "Ttl Pts Win"
    , "Ttl Pts Win Rk"
    , "Win Ttl"
    , "Loss Ttl"
    , "W/L Rk"
    , "Ttl Pts"
    , "Ttl Pts Rk"
    FROM prod.reg_season_results
    WHERE "Week" = (SELECT max("Week") FROM prod.reg_season_results)
    """
    return DatabaseCursor().copy_from_psql(query)


class DatabaseCursor(object):
    def __init__(self):
        """
        Import database credentials

        credential_file = path to private yaml file
        kwargs = {option_schema: "raw"}
        """
        credential_file = Path("/home/cuddebtj/Documents/Python/mom_weekly_rankings_email/mom_weekly_rankings_email/assets/private.yaml")

        try:
            with open(credential_file) as file:
                self.credentials = yaml.load(file, Loader=yaml.SafeLoader)

        except Exception as e:
            logger.critical(f'Error: {e}', exc_info=True)

        self.db_url = self.credentials["heroku_db_url"]

    def __enter__(self):
        """
        Set up connection and cursor
        """
        try:
            self.conn = psycopg2.connect(
                self.db_url,
                sslmode="require",
            )

        except Exception as e:
            logger.critical(f'Error: {e}', exc_info=True)

        self.cur = self.conn.cursor()

        return self.cur

    def __exit__(self, exc_result):
        """
        Close connection and cursor

        exc_results = bool
        """
        try:
            if exc_result == True:
                self.conn.commit()

            self.cur.close()
            self.conn.close()

        except Exception as e:
            logger.critical(f'Error: {e}', exc_info=True)

    def copy_from_psql(self, query):
        """
        Copy data from Postgresql Query into
        Pandas dataframe
        https://towardsdatascience.com/optimizing-pandas-read-sql-for-postgres-f31cd7f707ab

        query = "select * from raw.test"
        """
        cursor = self.__enter__()

        sql_query = f"COPY ({query}) TO STDOUT WITH (FORMAT CSV, HEADER TRUE);"
        buffer = StringIO()

        try:
            cursor.copy_expert(sql_query, buffer)
            buffer.seek(0)
            df = pd.read_csv(buffer)
            self.__exit__(exc_result=True)

            return df

        except Exception as e:
            logger.error(f'Error: {e}', exc_info=True)
