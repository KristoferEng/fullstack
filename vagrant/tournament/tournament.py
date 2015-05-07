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

    # Delete all matches.
    c.execute('delete from matches')

    pg.commit()
    pg.close()


def deletePlayers():
    """Remove all the player records from the database."""
    pg = connect()
    c = pg.cursor()

    # Delete all players.
    c.execute('delete from players')

    pg.commit()
    pg.close()


def countPlayers():
    """Returns the number of players currently registered."""
    pg = connect()
    c = pg.cursor()

    # Count total players.
    c.execute('select count(*) from players')

    count = c.fetchall()
    pg.close()
    return count[0][0]


def registerPlayer(name):
    """Adds a player to the tournament database."""
    pg = connect()
    c = pg.cursor()

    # Insert new player with name variable.
    c.execute("insert into players(name) values(%s)", (name,))

    pg.commit()
    pg.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins."""
    pg = connect()
    c = pg.cursor()

    # Run query to get id, name, wins, and matches played.
    c.execute("select id, name, (select count(*) from matches where players.id \
              = winner_id) as wins, (select count(*) from matches where \
              players.id IN (winner_id, loser_id)) as matches from players \
              order by wins desc")

    win_records_list = c.fetchall()
    return win_records_list


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players."""
    pg = connect()
    c = pg.cursor()

    # Insert winner and loser id's for match into matches
    c.execute("insert into matches(winner_id, loser_id) VALUES(%s, %s)",
              (winner, loser,))

    pg.commit()
    pg.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match."""

    # Get current standings to select swiss pairings.
    current_standings = playerStandings()

    pairs = []

    # Loop through standings by two to append the swiss pairings to list pairs.
    for i in range(0, len(current_standings), 2):
        opponent1 = current_standings[i]
        opponent2 = current_standings[i+1]
        pairs.append([opponent1[0], opponent1[1], opponent2[0], opponent2[1]])
    return pairs
