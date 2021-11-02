# -*- coding: utf-8 -*-
from genericpath import exists
import os
import logging
from appdirs import AppDirs
from random import randint, choice


logdir = AppDirs("craps", "gamelogs").user_log_dir


def create_logger(game_id, level=logging.INFO):
    # Create a custom logger
    logger = logging.getLogger(game_id)
    logger.setLevel(level)

    # Create handlers
    c_handler = logging.StreamHandler()
    c_handler.setLevel(level)
    f_handler = logging.FileHandler(f"{logdir}/{game_id}")
    f_handler.setLevel(level)

    # Create formatters and add it to handlers
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)
    logger.addHandler(c_handler)

    return logger

def purge_logs():
    """Empty the contents of the logs folder each time this package is imported.
    This function is called on craps.__init__
    
    This is to prevent clutter. If you'd like to keep your logs, save them someplace else.
    """
    os.makedirs(logdir, exist_ok=True)
    for f in [f for f in os.listdir(logdir)]:
        os.remove(f"{logdir}/{f}")

class TestRoll():
    def __init__(self, override=(None, None)):
        self.die_one   = override[0] or randint(1,6)
        self.die_two   = override[1] or randint(1,6)
        self.result    = self.die_one + self.die_two

def p_prob():
    """
    Returns a series with the probability of rolling x:
        where x in range 2 through 12
    """
    p  = [(x, y) for x in range(1,7) for y in range(1,7)]
    p  = [x+y for x in range(1,7) for y in range(1,7)]
    return {x: p.count(x)/len(p) for x in range(2,13)}

def prob_of_craps():
    """
    Calculates the probability of rolling 2, 3 or 12
    """
    p = p_prob()
    return p[[2,3,12]].sum()

def prob_of_x(x):
    """
    Calculates the probability of rolling an x:
        where x in range 2 through 12
    """
    assert x in range(2,13)
    return p_prob().loc[x]

def random_craps():
    """
    Generates a rando craps roll object
    """
    p  = [(x, y) for x in range(1,7) for y in range(1,7)]
    p  = [x for x in p if x[0]+x[1] in [2,3,12]]
    return TestRoll(override=choice(p))

def random_point():
    """
    Generates a random non craps roll object
    """
    p  = [(x, y) for x in range(1,7) for y in range(1,7)]
    p  = [x for x in p if x[0]+x[1] in [4,5,6,8,9,10]]
    return TestRoll(override=choice(p))

#%% Depricated to remove pandas dependency
# def sample_role_dist(n=100):
#     """
#     Plots a sample of n dice rolls against the true population odds
#     """
#     # Roll some die
#     rolls = [TestRoll() for r in range(n)]
#     rolls = [r.result for r in rolls]
#     df    = pd.DataFrame(rolls, columns=['roll'])
#     df    = df.reset_index().rename(columns={'index': 'sample'})
    
#     # Count the requencies in the sample and compater to population probabilities
#     freq = df.groupby(['roll']).count() / n
#     freq['p_prob'] = p_prob()
       
#     return freq * n


# def plot_some_samples(n=1, rolls=100):
#     """
#     Plot some sample rolls to visualize random sets vs the population probability
    
#         n     = Number of rolls sets to plot
#         rolls = Number of rolls per set
        
#     """
#     for i in range(n):
#         sample_role_dist(rolls).plot.bar()

    
