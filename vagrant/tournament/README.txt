#Note to self: Do not change the ‘fullstack’ root folder name. Otherwise, when in vagrant it will not work.

Steps to Run

1. Open terminal.
2. Change directory to tournament folder.
3. Type ‘vagrant up’ in cmd line.
4. Type ‘vagrant ssh’ in cmd line.
5. Cd /vagrant/tournament.
5. Type psql.
6. Type CREATE DATABASE tournament;.
7. Type crtl + z.
8. Type psql tournament.
9. Type create tables players/matches from tournament.sql.
10. Type crtl + z.
11. Type python tournament_test.py or any python code to test using tournament.py.