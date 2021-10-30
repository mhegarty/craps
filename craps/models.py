# -*- coding: utf-8 -*-
# Mike Hegarty (Github: mhegarty)

from uuid import uuid4
from random import randint
from .utils import create_logger


class Game():
    """A Single Game Session

    simulation_id (int) : The simulation
    arrival_cash (int)  : How much money to start with
    minimum_bet (int)   : The table minimum. Most places are $10
    puck (int)          : Location of the puck or None if off

    rolls (list) : List of the Roll objects in this game
    bets (list)  : List of Bet objects in this game

    A Game consists of a series of bets and rolls and follows this sequence:

    1) Instantiate a game with a defined amount of arrival cash, table minimum, and max odds.

    2) Bet. Each bet is validated when it instantiated 
            eg. no place bets when puck is on
                set the point for odds bets
                set the game id

    3) Roll. Role the dice and get a result.

    4) Evaluate. Check each bet and update payout, working, and settled attributes."""
    def __init__(self, **kwargs):
        self._id     = None
        self.logger  = create_logger(self.id)
        self.history = []
        
        self.allow_credit_rail = False  # Allow borrowing?
        
        self.arrival_cash  = 1000.
        self.minimum_bet   = 10.  # The table minimum bet (typically $10)
        self.max_odds      = 10.  # The table limit on odds bets (typically 10x come or pass)
        
        self.puck  = None
        self.rolls = []
        self.bets  = []

        self.logger.info(f'[Table] Welcome to the table shooter!')

    
    @property
    def id(self):
        if not self._id:  # id property getter commits the game
            self._id = str(uuid4())
            # response = tbl.put_item( Item={
            #             'game': self._id,
            #             'user': get_current_user()} )
        return self._id
          
    def callout(self):
        for bet in self.unsettled_bets:
            self.logger.info(f'[Table] {bet.call_out()}')

    def roll(self, override=None):
        """Rolls th dice"""
        # Log 
        self.logger.info(f"[Table] The shooter is ready, the point is {self.puck or 'off'}")
        self.callout()

        # Add a role      
        roll = override or Roll(self)
        self.rolls.append(roll)
        
        # Call it out 
        self.logger.info(f"[Roll] {roll.call_out() or 'No Action'}")
        
        # Evaluate bets
        self.evaluate_bets()
        
        # Count up the rail
        self.logger.info(f"[Rail] You have {self.rail_balance} on the rail")
        
        # Set the puck
        if (not self.puck) and (roll.result in [4,5,6,8,9,10]):            
            self.puck = roll.result  # Turn the puck on
                    
        elif (not self.puck) and (roll.result in [2,3,7,11,12]):
            self.puck = None  # Craps or PassLine Winner. Keep the puck off
        
        elif (self.puck) and (roll.result == 7):
            self.puck = None  # 7 out. Take the puck off
        
        elif (self.puck) and (roll.result == self.puck):
            self.puck = None  # Winner. Take the puck off
        
        # Update history
        self.history += [{'roll_result': self.last_roll.result,
                          'net_worth': self.net_worth}]
    

    def _bet(self, bet):
        """Add a bet"""
        
        # Validate the bet
        # Make sure there is enough money on the rail
        if (not self.allow_credit_rail) and (bet.amount > self.rail_balance):
             raise AssertionError('You are bankrupt. Bet rejected')
        
        # Catch illogical come bet, move it to the pass line
        if (not self.puck) & (type(bet) is ComeBet):
            raise AssertionError('You are placing a come bet with the puck off. Moving to the line.')
        
        # Reject point odds bets without a come on point
        if type(bet) is PointOddsBet:
            working_come_points = [bet.point for bet in self.unsettled_bets if (type(bet) is ComeBet)]
            if bet.point not in working_come_points:
                raise AssertionError('You tried to place an odds bet with no come. Bet amount set to zero')

        # Bet has been validated
        # Assign the bet to this game
        bet.game = self

        # Set the Point for Pass, Lineodds
        if (self.puck) and (type(bet) in [PassBet, LineOddsBet]):   # set the point for
            bet.point = self.puck                                   # pass, lineodds

        # Append the bet
        self.bets.append(bet)

        # Logs
        self.logger.info(f"[Bet] You made a {bet.type} on {bet.point or'the box'} for {bet.amount}")
        self.logger.info(f"[Rail] You have {self.rail_balance} on the rail")        

    def bet(self, bet):
        """Add a bet"""
        try:
            self._bet(bet)
        except AssertionError as e:
            self.logger.info(f"[Bet] {e}")

    def evaluate_bets(self):  # evaluate working bets
        for bet in self.working_bets:
            bet.evaluate(self.last_roll)
    
    
    @property
    def last_roll(self):      # get the last roll 
        return self.rolls[-1] # note to self... go back and make sure ordering is handled correctly
    
    @property
    def working_bets(self):   # get collection of working bets
        return [bet for bet in self.bets if bet.working]

    @property
    def idle_bets(self):   # get collection of working bets
        return [bet for bet in self.bets if (not bet.working) & (not bet.settled)]

    @property
    def unsettled_bets(self):   # get collection of working bets
        return [bet for bet in self.bets if not bet.settled]

    @property
    def total_amounts_working(self): # how much do i have working on the table?
        return sum([bet.amount for bet in self.working_bets])

    @property
    def total_amounts_idle(self): # how much do i have not working and not settled on the table?
        return sum([bet.amount for bet in self.idle_bets])

    @property
    def total_amounts_on_table(self): # how much do i on the table
        return self.total_amounts_working + self.total_amounts_idle

    @property
    def pnl(self):  # Realized gain or loss
        return sum([bet.pnl for bet in self.bets])
    
    @property
    def rail_balance(self):  # Realized gain or loss
        return self.arrival_cash + self.pnl - self.total_amounts_on_table

    @property
    def net_worth(self):
        return self.rail_balance + self.total_amounts_on_table

        

#%% BET
class Bet():
    """A Bet superclass
    
    Bets have an amount and a payout. Once the
    payout attribute is set, the bet is settled
    and the pnl becomes payout - amount.
    
    """
    def __init__(self, amount, point=None):
        
        self.id   = str(uuid4())
        self.game = None

        self.amount = amount
        self.point  = point

        self._payout = None
        self.working = True
        self.settled = False

    @property
    def type(self):
        return str(type(self)).split('.')[-1][:-2]

    @property
    def payout(self):
        return self._payout

    @payout.setter  # Close up the bet once payout is set
    def payout(self, value):
        self._payout = value
        self.working = False
        self.settled = True

    
    @property
    def pnl(self):
        return self.payout - self.amount if self.settled else 0.

    def evaluate(self):
        # Log the payout amount
        if self.payout is not None:
            self.game.logger.info('[Payout] ' + '{} on {} {} {}'.format(self.type,
                self.point or 'the box',
                'paid out' if self.payout > 0 else 'lost', 
                self.payout if self.payout > 0 else self.amount))
        
    
    def call_out(self):
        return '{t} for {a} is {w} on {p}'.format(
                    t=self.type, a=self.amount, 
                    w=('working' if self.working else 'not working'), 
                    p=self.point or 'the box')

    def __repr__(self) -> str:
        return f"{self.type}: amount={self.amount}, point={self.point}, payout={self.payout}, working={self.working}"

class PassBet(Bet):
    """A Pass bet is"""
    def __init__(self, *args, **kwargs):
        super(PassBet, self).__init__(*args, **kwargs)

 
    def evaluate(self, roll):
        
        # Payouts
        if (not self.point) and (roll.result in [7, 11]):
            self.payout = self.amount * 2            # Winner, Pay the line
            
        elif (self.point) and (roll.result == self.point):
            self.payout = self.amount * 2            # Winner!
        
        elif (self.point) and (roll.result == 7):
            self.payout = 0                          # 7 Out

        elif (not self.point) and (roll.result in [2, 3, 12]):
            self.payout = 0                          # Craps

        # Set the point
        if (not self.point) and (roll.result in [4,5,6,8,9,10]):
            self.point = roll.result
        
        # Log the result
        super(PassBet, self).evaluate()


class ComeBet(Bet):  # a Come Bet is just a line bet whilst the puck is on
    """A Come bet is"""
    def __init__(self, *args, **kwargs):
        super(ComeBet, self).__init__(*args, **kwargs)

    def evaluate(self, roll):
                          
        # Payouts
        if (not self.point) and (roll.result in [7, 11]):
            self.payout = self.amount * 2            # Winner
            
        elif (self.point) and (roll.result == self.point):
            self.payout = self.amount * 2            # Winner!
        
        elif (self.point) and (roll.result == 7):
            self.payout = 0                          # 7 Out

        elif (not self.point) and (roll.result in [2, 3, 12]):
            self.payout = 0                          # Craps

        # Set the point
        if (not self.point) and (roll.result in [4,5,6,8,9,10]):
            self.point = roll.result
            self.game.logger.info('[Bet] '+ "{t} for {a} was moved to the {r}".format(
                    t=self.type, a=self.amount, r=roll.result))
            

        # Log the result
        super(ComeBet, self).evaluate()
    

class LineOddsBet(Bet):
    """Line Odds are"""
    def __init__(self, amount, point=None):
        super().__init__(amount, point=point)

    def evaluate(self, roll):
        
        # Validate working
        self.point   = self.game.puck          # Point is always the game puck
        self.working = self.point is not None  # If point is set it it working
        if not self.working:                   # Dont go to payouts if not working
            return
               
        # Payouts
        if (roll.result == self.point):      # Winner!
            self.payout = self.amount + self.amount * \
                {4:  2/1, 5: 3/2, 6: 6/5, 10: 2/1, 9: 3/2, 8: 6/5}[roll.result]      
        
        elif (roll.result == 7):
            self.payout = 0                   # 7 Out
        
        # Log the result
        super(LineOddsBet, self).evaluate()


class PointOddsBet(LineOddsBet):  
    """Point Odds are"""
    def __init__(self, amount, point):
        super(PointOddsBet, self).__init__(amount, point)
    
    
    def evaluate(self, roll):
        
        # Validate working
        self.working = self.game.puck is not None  # If point is set it is working
               
        # Payouts
        if (self.working) and (roll.result == self.point):  # Winner!
            self.payout = self.amount + self.amount * \
                {4:  2/1, 5: 3/2, 6: 6/5, 10: 2/1, 9: 3/2, 8: 6/5}[roll.result]     
        
        elif (self.working) and (roll.result == 7):         # 7 Out
            self.payout = 0                
        
        elif (not self.working) and (roll.result == 7):     # 7 on a comeout roll, push
            self.payout = self.amount              
        
        # # Log the result
        super(LineOddsBet, self).evaluate()

#%% ROLL
class Roll():
    """Roll class is a unique roll when it is instantiated."""
    def __init__(self, game, override=(None, None)):
        
        self.id        = str(uuid4())
        self.game      = game
        self.puck      = game.puck
        self.die_one   = override[0] or randint(1,6)
        self.die_two   = override[1] or randint(1,6)
        self.result    = self.die_one + self.die_two

    def call_out(self):
        self.game.logger.info(f"[Roll] Shooter rolled {self.result}")
             
        # 7 out
        if self.puck and self.result == 7:
            return "7 out. Take the line. Pay the dont's and the last come"
        
        # call out a point setter                            
        if (not self.puck) and (self.result in [4,5,6,8,9,10]):
            return 'The point is {}'.format(self.result)
        
        # Pass line Winner
        if (not self.puck) and (self.result in [7, 11]):
            return "Winner, {}. Take the dont's and pay the line.".format(self.result)
 
        # Winner
        if self.result == self.puck:
            return "Winner!!, {}".format(self.result)
        
        # Craps Loser
        if (not self.puck) and (self.result in [2,3,12]):
            return f"{self.result} Craps. Take the line. Come again."
        
        # Craps Backup, pay the field
        if (self.result in [2, 12]):
            return "{} double the field".format(self.result)
        
        # Field Backup, pay the field
        if (self.result in [3, 4, 9, 10, 11]):
            return "{} pay the field".format(self.result)

        # 6 8 backup
        if (self.result in [6, 8]):
            return "{}+{}={} {}".format(
                    self.die_one,
                    self.die_two,
                    self.result, 
                    'the hard way' if self.die_one==self.die_two else 'came easy')
        
        # 5 backup
        if (self.result == 5):
            return "No field 5"

