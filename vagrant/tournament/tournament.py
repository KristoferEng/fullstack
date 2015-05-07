# !/usr/bin/env python
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    pg = connect()
    c = pg.cursor()
    c.execute('delete from matches')
    pg.commit()
    pg.close()


def deletePlayers():
    """Remove all the player records from the database."""
    pg = connect()
    c = pg.cursor()
    c.execute('delete from players')
    pg.commit()
    pg.close()


def countPlayers():
    """Returns the number of players currently registered."""
    pg = connect()
    c = pg.cursor()
    c.execute('select count(*) from players')
    count = c.fetchall()
    pg.close()
    return count[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database."""
    pg = connect()
    c = pg.cursor()
    c.execute("insert into players(name) values(%s)", (name,))
    pg.commit()
    pg.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins."""
    pg = connect()
    c = pg.cursor()
    c.execute("select id, name, wins, matches from players order by wins desc")
    win_records_list = c.fetchall()
    return win_records_list


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players."""
    pg = connect()
    c = pg.cursor()
    c.execute("insert into matches(winner_id, loser_id) VALUES(%s, %s)", (winner, loser,))
    c.execute("update players set matches = matches+1 where id =%s", (loser,))
    c.execute("update players set wins=wins+1, \matches = matches+1 where id =%s", (winner,))
    pg.commit()
    pg.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match."""
    current_standings = playerStandings()

    pairs = []

    for i in range(0, len(current_standings), 2):
        opponent1 = current_standings[i]
        opponent2 = current_standings[i+1]
        pairs.append([opponent1[0], opponent1[1], opponent2[0], opponent2[1]])
    return pairs
