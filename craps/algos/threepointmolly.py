""" The Three Point Molly Strategy
This is a fun way to play craps. Some people have suggested that 
playing this strategy gives the house its lowest edge of any game 
in the casino. The strategy consists of playing the line and making 
successive come bets until you have three points "covered".

The algorithm in psudo code is as follows, where `points_covered` 
is the count of numbers for which you have bets placed.

If it is a come out roll, then make a PassBet

Else, for any other roll.

- If you don't already have odds on your pass bet, then add them with a LineOddsBet
- If you have a come bet that has been moved to a point but does not yet have odds, 
   then add odds by making a PointOddsBet on that point.
- If you have less than three points_covered, then make a ComeBet

Finally, roll
"""

from craps import Game, PassBet, LineOddsBet, ComeBet, PointOddsBet


# Setting up default parameters for a simulation.
arrival_cash   = 1000 # How much are you bringing to the table?
rolls          = 100  # How many rolls to play?
bet_unit       = 10   # How much to bet on line bets and come bets?
x_odds         = 2    # How much odds to bet (typical casino limit is 10x)
loglevel       = 50   # We don't want any logs

# Building the algo for the Three Point Molly strategy
# Following the psudo code as a guide, we write the logic to step through before each roll. 
def betting_algo(g):
    
    # If it is a come out roll, then make a PassBet
    # ie. If the puck is off and I have no line bet placed, make a pass bet
    passbets = [bet for bet in g.unsettled_bets if (type(bet) is PassBet)]
    if (not g.puck) and (len(passbets)==0):
        g.bet(PassBet(bet_unit))

    # If you don't already have odds on your pass bet, then add them with a LineOddsBet
    # ie. If the puck is on but no odds on the line, make an odds bet
    lineoddsbets = [bet for bet in g.unsettled_bets if (type(bet) is LineOddsBet)]
    if (g.puck) and (len(lineoddsbets)==0):
            g.bet(LineOddsBet(bet_unit*x_odds))  # bet the line odds

    # If you have a come bet that has been moved to a point but does not yet have odds, 
    #    then add odds by making a PointOddsBet on that point.    
    # ie. If the puck is on and I have a come bet on point but no odds, bet the odds
    if g.puck:
        set_come_bets = [bet for bet in g.unsettled_bets if (type(bet) is ComeBet) and (bet.point)]
        for comeBet in set_come_bets:
            odds = [bet for bet in g.unsettled_bets if (type(bet) is PointOddsBet) and (bet.point == comeBet.point)]
            if not any(odds):
                g.bet(PointOddsBet(bet_unit*x_odds, comeBet.point))

    # If you have less than three `points_covered`, then make a `ComeBet`
    # ie. If the point is set, and no comebet, and I have less than 3 points, place a come bet
    if g.puck:
        set_comebets   = [bet for bet in g.unsettled_bets if (type(bet) is ComeBet) and (bet.point)]
        unset_comebet  = [bet for bet in g.unsettled_bets if (type(bet) is ComeBet) and (not bet.point)]
        if (g.puck) and (not any(unset_comebet)) and (len(set_comebets) < 2):
            g.bet(ComeBet(bet_unit))


# Now build a game simulation function that uses the above betting algo. 
def simulate_game():
    """Simulates a game of craps. Optionally pass a loglevel to control stream"""
    g = Game(arrival_cash=arrival_cash, loglevel=loglevel)
    # Make rolls
    for n in range(rolls):  # Using the number of rolls defined in the game parameters earlier.
        betting_algo(g)
        g.roll()
    # Return the comleted game history
    return g.history
