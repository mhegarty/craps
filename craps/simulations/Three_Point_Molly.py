from craps.models import Simulation, Game, PassBet, LineOddsBet, ComeBet, PointOddsBet
from craps.database import db_session
import multiprocessing as mp


# Instantiate the simulation class
s = Simulation()
s.num_of_games   = 10000
s.rolls_per_game = 100
s.bet_unit       = 10

# Parameter. How many times pass/come to place on odds
x_odds       = 10.  # Typical casino limit is 10x
arrival_cash = 1000  # How much are you bringing to the table?

# Dynamic Name
s.description     = "Three point molly with {}x odds and {} arrival cash".format(int(x_odds), arrival_cash)


def run_one():
    
    # Set a the Game    
    g = Game()
    g.arrival_cash = arrival_cash
    
    # Betting Algorithm
    for i in range(s.rolls_per_game):
        
        # If the puck is off and I have no line bet placed, make a pass bet
        passbets = [bet for bet in g.unsettled_bets if (type(bet) is PassBet)]
        if (not g.puck) and (len(passbets)==0):
            g.bet(PassBet(s.bet_unit))

        # If the puck is on but no odds on the line
        lineoddsbets = [bet for bet in g.unsettled_bets if (type(bet) is LineOddsBet)]
        if (g.puck) and (len(lineoddsbets)==0):
            g.bet(LineOddsBet(s.bet_unit*x_odds))  # bet the line odds

        # If the point is set, and no comebet, and I have less than 3 points (less than two come on point), place a come bet
        if g.puck:
            set_comebets   = [bet for bet in g.unsettled_bets if (type(bet) is ComeBet) and (bet.point)]
            unset_comebet  = [bet for bet in g.unsettled_bets if (type(bet) is ComeBet) and (not bet.point)]
            if (g.puck) and (not any(unset_comebet)) and (len(set_comebets) < 2):
                g.bet(ComeBet(s.bet_unit))
        
        # If the puck is on and I have a come bet on point but no odds, bet the odds
        if g.puck:
            set_come_bets = [bet for bet in g.unsettled_bets if (type(bet) is ComeBet) and (bet.point)]
            for come in set_come_bets:
                odds = [bet for bet in g.unsettled_bets if (type(bet) is PointOddsBet) and (bet.point == come.point)]
                if not any(odds):
                    g.bet(PointOddsBet(s.bet_unit*x_odds, come.point))
        
        # Ready, now Roll!
        g.roll()
    
    # Return the completed game
    return g


if __name__ == '__main__':
    pool  = mp.Pool()                                             # Multiprocess pool uses all available cores
    games = [pool.apply(run_one) for x in range(s.num_of_games)]  # Run the games
    for g in games:
        s.games.append(g)    # Add the games to the simulation
    db_session.add(s)        # Add the simulation to the session
    db_session.commit()      # Commit the session
