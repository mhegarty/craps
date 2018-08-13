# -*- coding: utf-8 -*-

from craps.models import Roll
import pandas as pd


def p_prob():
    """
    Returns a series with the probability of rolling x:
        where x in range 2 through 12
    """
    p  = [(x, y) for x in range(1,7) for y in range(1,7)]
    p  = [x+y for x in range(1,7) for y in range(1,7)]
    p  = [(x,p.count(x)/len(p)) for x in range(2,13)]
    ps = pd.DataFrame(p, columns=['result', 'prob']).set_index('result')['prob']
    return ps


def sample_role_dist(n=100):
    """
    Plots a sample of n dice rolls against the true population odds
    """
    # Roll some die
    rolls = [Roll() for r in range(n)]
    rolls = [r.result for r in rolls]
    df    = pd.DataFrame(rolls, columns=['roll'])
    df    = df.reset_index().rename(columns={'index': 'sample'})
    
    # Count the requencies in the sample and compater to population probabilities
    freq = df.groupby(['roll']).count() / n
    freq['p_prob'] = p_prob()
       
    return freq * n


def plot_some_samples(n=1, rolls=100):
    """
    Plot some sample rolls to visualize random sets vs the population probability
    
        n     = Number of rolls sets to plot
        rolls = Number of rolls per set
        
    """
    for i in range(n):
        sample_role_dist(rolls).plot.bar()

    
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
    r  = pd.np.random.choice(range(len(p)))
    return Roll(override=p[r])

def random_point():
    """
    Generates a random non craps roll object
    """
    p  = [(x, y) for x in range(1,7) for y in range(1,7)]
    p  = [x for x in p if x[0]+x[1] in [4,5,6,8,9,10]]
    r  = pd.np.random.choice(range(len(p)))
    return Roll(override=p[r])

    
