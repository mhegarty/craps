from craps.models import Simulation, Game, PassBet, LineOddsBet
from craps.database import db_session
import multiprocessing as mp


# Instantiate the simulation class
s = Simulation()
s.num_of_games   = 5
s.rolls_per_game = 100
s.bet_unit       = 10

# Parameter. How many times pass/come to place on odds
x_odds = 2.  # Typical casino limit is 10x

# Dynamic Name
s.description     = "Pass line with {}x odds".format(int(x_odds))


def run_one():
    
    # Set up he Game    
    g = Game() 
    g.log_game()
    
    # Betting Algorithm
    for i in range(s.rolls_per_game):  
        
        # For each roll, place bets
        if len(g.working_bets)==0:     # If there are no working bets
            g.bet(PassBet(s.bet_unit))    # Make a place bet

        if g.puck and len(g.working_bets)==1:  # If the puck is set and you have bet the pass
            g.bet(LineOddsBet(s.bet_unit*x_odds))  # Bet the line odds
        
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
        



