import psycopg2
import yaml
import pandas as pd
from io import StringIO
from pathlib import Path

def get_data(path):
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
    , "Avg Pts"
    , "Ttl Opp Pts"
    , "Avg Opp Pts"
    , "Wk W/L"
    , "Wk Pts W/L"
    , "Wk Pts"
    , "Wk Pts Rk"
    , "Opp Team"
    , "Opp Manager"
    , "Opp Wk Pts"
    , "Opp Wk Pts Rk"
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
        credential_file = list(Path().cwd().glob("**/private.yaml"))[0]

        with open(credential_file) as file:
            self.credentials = yaml.load(file, Loader=yaml.SafeLoader)

        self.db_url = self.credentials["heroku_db_url"]

    def __enter__(self):
        """
        Set up connection and cursor
        """
        self.conn = psycopg2.connect(
            self.db_url,
            sslmode="require",
        )
        self.cur = self.conn.cursor()

        return self.cur

    def __exit__(self, exc_result):
        """
        Close connection and cursor

        exc_results = bool
        """

        if exc_result == True:
            self.conn.commit()

        self.cur.close()
        self.conn.close()

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

        cursor.copy_expert(sql_query, buffer)
        buffer.seek(0)
        df = pd.read_csv(buffer)
        self.__exit__(exc_result=True)

        return df
