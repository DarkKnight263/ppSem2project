import datetime as dt
import sqlite3
import requests
import prettytable
import matplotlib.pyplot as plt
import numpy as np


class backend:
    """
    homeCurrency can be: "INR", "EUR", "GBP" or "USD"
    numOfDOGEToBuy is the number of DOGE you are willing to buy with the total budget of moneyToBuyDOGE
    numOfDOGEToBuy should never be 0 otherwise it will lead to ZeroDivisionError
    same for LTC as well
    """

    def __init__(self, homeCurrency: str, numOfDOGEToBuy: float, moneyToBuyDOGE: float, numOfLTCToBuy: float, moneyToBuyLTC: float) -> None:
        self.homeCurrency: str = homeCurrency
        self.numOfDOGEToBuy: float = numOfDOGEToBuy
        self.moneyToBuyDOGE: float = moneyToBuyDOGE
        self.numOfLTCToBuy: float = numOfLTCToBuy
        self.moneyToBuyLTC: float = moneyToBuyLTC
        print(f"backend object constructed with {homeCurrency}, {numOfDOGEToBuy}, {moneyToBuyDOGE}, {numOfLTCToBuy}, {moneyToBuyLTC}\n\n")

    def fetchRates(self, date: str = "latest") -> dict[str, str | float]:
        url: str = f"https://api.exchangerate.host/{date}"

        # GET FIAT CURRENCY EXCHANGE RATES
        response: requests.Response = requests.get(url, params={"base": "USD", "symbols": "INR,EUR,GBP", "places": 4}, timeout=10)
        data: dict = response.json()
        print(f"{response} received for date {date} as {data}\n")
        rates: dict[str, float] = data["rates"]  # EXTRACT RATES DICT FROM JSON OBJ
        # CREATE ENTRY DICT WITH TIMESTAMPS + FIAT CURRENCY RATES
        entry: dict[str, str | float] = {
            "time": data["date"],
            "INR": rates["INR"],
            "EUR": rates["EUR"],
            "GBP": rates["GBP"],
        }

        # GET CRYPTO CURRENCY EXCHANGE RATES
        response = requests.get(
            url,
            params={"base": "USD", "source": "crypto", "symbols": "DOGE,LTC"},
            timeout=10,
        )
        data = response.json()
        print(f"{response} received for date {date} as {data}\n")
        rates = data["rates"]  # EXTRACT RATES DICT FROM JSON OBJ
        # APPEND THE RATE TO ENTRY DICT
        entry["DOGE"] = rates["DOGE"]
        entry["LTC"] = rates["LTC"]
        print(f"extracted {entry} from response\n\n\n\n")
        return entry
        # FORMAT {TIMESTAMP, FIAT RATE, CRYPTO RATE}
        # SAMPLE {'time': '2023-04-24', 'INR': 82.0465, 'EUR': 0.911, 'GBP': 0.8042, 'DOGE': 0.06574, 'LTC': 3.6e-05}

    def compareTarget(self) -> dict[str, bool]:  # RETURNS dict with keys "DOGE" and "LTC and bool values"
        rates: dict[str, str | float] = self.fetchRates()
        res: dict[str, bool] = {"DOGE": False, "LTC": False}
        if self.homeCurrency != "USD":
            res["DOGE"] = self.moneyToBuyDOGE / (rates[self.homeCurrency] * self.numOfDOGEToBuy) >= rates["DOGE"]
            res["LTC"] = self.moneyToBuyLTC / (rates[self.homeCurrency] * self.numOfLTCToBuy) >= rates["LTC"]
        else:
            res["DOGE"] = self.moneyToBuyDOGE / self.numOfDOGEToBuy >= rates["DOGE"]
            res["LTC"] = self.moneyToBuyLTC / self.numOfLTCToBuy >= rates["LTC"]
        return res

    def ratesThisWeek(self) -> list[dict[str, str | float]]:
        today: dt.date = dt.date.today()
        ratesThisWeekAsListOfDicts: list[dict[str, str | float]] = list(dict())
        cachedRatesdb: sqlite3.Connection = sqlite3.connect("cachedRates.db")
        cursor: sqlite3.Cursor = cachedRatesdb.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS cache (
                timestamp text,
                INR real,
                EUR real,
                GBP real,
                DOGE real,
                LTC real
            )"""
        )

        cursor.execute("SELECT timestamp FROM cache")
        timestamps: list[str] = [row[0] for row in cursor.fetchall()]

        for i in range(7, -1, -1):
            date = str(today - dt.timedelta(days=i))
            if date not in timestamps:  # DONT FETCH RATES AGAIN IF THE TIMESTAMP CACHED IN DB
                ratesThisWeekAsListOfDicts.append(self.fetchRates(date))
            else:
                print(f"rates for {date} already in sqlite3 cache")

        cachedRatesdb.commit()
        cachedRatesdb.close()
        return ratesThisWeekAsListOfDicts

    def dbHandler(self) -> None:
        cachedRatesdb: sqlite3.Connection = sqlite3.connect("cachedRates.db")
        weekRates: list[dict[str, str | float]] = self.ratesThisWeek()
        cursor: sqlite3.Cursor = cachedRatesdb.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS cache (
                timestamp text,
                INR real,
                EUR real,
                GBP real,
                DOGE real,
                LTC real
            )"""
        )
        if len(weekRates) != 0:
            print(f"{weekRates} will be cached in sqlite\n\n")
        for dc in weekRates:
            cursor.execute(f"INSERT INTO cache VALUES ('{dc['time']}', {dc['INR']}, {dc['EUR']}, {dc['GBP']}, {dc['DOGE']}, {dc['LTC']})")
            print(f"successfully cached {dc}")

        cachedRatesdb.commit()
        cachedRatesdb.close()
        self.printDB()

    def printDB(self) -> None:
        cachedRatesdb: sqlite3.Connection = sqlite3.connect("cachedRates.db")
        cursor: sqlite3.Cursor = cachedRatesdb.cursor()
        cursor.execute("SELECT * FROM cache")
        table: prettytable.PrettyTable | None = prettytable.from_db_cursor(cursor)
        print(table)

    def plot(self, coin: str) -> None:  # coin can be "DOGE" or "LTC"
        cachedRatesdb: sqlite3.Connection = sqlite3.connect("cachedRates.db")
        cursor: sqlite3.Cursor = cachedRatesdb.cursor()
        cursor.execute(f"SELECT timestamp, {coin} FROM cache")
        result: list[tuple[str, float]] = cursor.fetchall()
        timestamps: np.ndarray[str, np.dtype[np.string_]] = np.array([result[0] for result in result])
        coinRates: np.ndarray[float, np.dtype[np.float64]] = np.array([result[1] for result in result])
        cachedRatesdb.close()
        plt.plot(timestamps, coinRates)
        plt.title(f"Historical Exchange Rate Of {coin} in USD")
        plt.xlabel("Timestamps (in days)")
        plt.ylabel(f"{coin}'s exchange rate (in USD)")
        plt.show()

    def test(self, rowsTBDel: int) -> None:
        cachedRatesdb: sqlite3.Connection = sqlite3.connect("cachedRates.db")
        cursor: sqlite3.Cursor = cachedRatesdb.cursor()

        cursor.execute("SELECT COUNT(*) FROM cache")
        num_rows: int = cursor.fetchone()[0]
        if num_rows >= rowsTBDel:
            cursor.execute(f"DELETE FROM cache WHERE ROWID IN (SELECT ROWID FROM cache ORDER BY ROWID DESC LIMIT {rowsTBDel})")
            cachedRatesdb.commit()
            print(f"Last {rowsTBDel} rows deleted successfully.")
            cachedRatesdb.commit()
        else:
            print(f"There are not enough rows in the table to delete the last {rowsTBDel} rows")

        cursor.execute("SELECT * FROM cache")
        table: prettytable.PrettyTable | None = prettytable.from_db_cursor(cursor)
        print(table)

        cachedRatesdb.close()


if __name__ == "__main__":
    instance = backend("USD", 1, 0.06575, 1, 73.141008)
    backend.dbHandler(self=instance)  # refresh the db
    backend.test(self=instance, rowsTBDel=4)  # remove bottom 4 entries
    backend.dbHandler(self=instance)  # refresh again to demonstrate caching as only 3 are still cached
    backend.plot(self=instance, coin="DOGE")
    backend.plot(self=instance, coin="LTC")
    print(backend.compareTarget(self=instance))
