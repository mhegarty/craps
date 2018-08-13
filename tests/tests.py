# -*- coding: utf-8 -*-

def test_utils():
    from craps.utils import p_prob
    assert p_prob().sum() == 1
    return True

def test_game_passbet_crapout():
    from craps.models import Game, PassBet
    from craps.utils import random_craps
    self = Game()
    self.bet(PassBet(10))
    assert len(self.working_bets) == 1
    self.roll(override=random_craps())
    assert len(self.working_bets) == 0
    assert self.bankroll == -10
    return True

def test_random_craps(n=1000):
    import pandas as pd
    from craps.utils import random_craps, p_prob
    rolls = [random_craps().result for x in range(n)]
    df    = pd.DataFrame(rolls, columns=['roll'])
    df    = df.reset_index().rename(columns={'index': 'sample'})
    freq  = df.groupby(['roll']).count() / n
    freq['p_prob'] = p_prob()
    freq['p_prob'] = freq['p_prob']/freq['p_prob'].sum()
    assert len(freq) == 3
    assert (freq['sample'] - freq['p_prob']).sum() < 0.01
    return True
        

def test_game_passbet_pointset():
    from craps.models import Game, PassBet
    from craps.utils import random_point
    self = Game()
    self.bet(PassBet(10))
    assert len(self.working_bets) == 1
    self.roll(override=random_point())
    assert self.puck == self.last_roll.result
    assert len(self.working_bets) == 1
    while self.puck:
        self.roll()
    if self.last_roll.result == 7:
        assert self.payouts == 0
        assert self.bankroll == -10
    else:
        assert self.payouts == 20
        assert self.bankroll == 10
    assert self.total_amounts_working == 0
    return True

if __name__ == '__main__':
    for i in range(100):
        assert test_utils()
        assert test_random_craps()
        assert test_game_passbet_crapout()
        assert test_game_passbet_pointset()


    