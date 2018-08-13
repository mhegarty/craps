# -*- coding: utf-8 -*-
"""
Mike Hegarty (Github: mhegarty)
Jul 2018
"""

from sqlalchemy import func, Column, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates
from craps.database import Base, db_session
from craps.logs import game_logger, no_logger
import pandas as pd
import warnings


class Game(Base):
    """
    :CLASS craps.models.Game
    """
    
    __tablename__ = 'games'
    
    _id           = Column(Integer, primary_key=True, autoincrement=True)
    simulation_id = Column(Integer, ForeignKey('simulations.id', onupdate="CASCADE", ondelete="CASCADE"))
    arrival_cash  = Column(Integer, default=200)
    minimum_bet   = Column(Integer, default=10)
    puck          = Column(Integer, default=None)
    description   = Column(Text,    default=None)
    
    rolls      = relationship("Roll", cascade="all, delete-orphan")
    bets       = relationship("Bet", cascade="all, delete-orphan")
    simulation = relationship("Simulation", cascade="save-update")
    
    log = no_logger()
    
    
    def __init__(self):
        
        self.allow_debit_rail = False
        
        db_session.add(self)
        db_session.commit()

    
    def log_game(self):                   # Turn on game logging
        self.log = game_logger(self)   # see craps.logs.game_logger()
        
    
    @hybrid_property
    def id(self):
        if not self._id:            # id property getter commits the game
            db_session.add(self)    # to the db in order to get the auto incremented
            db_session.commit()     # game id
        return self._id
    
    
    @validates("bets")
    def validate_bets(self, key, bet):   # bets validator runs on append events
        
        # Make sure there is enough money on the rail
        if (not self.allow_debit_rail) and (bet.amount > self.rail_balance):
             warnings.warn('You are bankrupt. Bet amount set to zero')
             bet.amount = 0
        
        if (not self.puck) & (type(bet) is ComeBet):      # Catch illogical comebest
            warnings.warn('You are placing a comebet with the puck off. Moving to the line.')
            bet = PassBet(bet.amount)
        
        # Reject point odds bets without a come on point
        if (type(bet) is PointOddsBet):
            working_come_points = [bet.point for bet in self.unsettled_bets if (type(bet) is ComeBet)]
            if bet.point not in working_come_points:
                warnings.warn('You tried to place an odds bet with no come. Bet amount set to zero')
                bet.amount = 0
        
        # Set the Point for Pass, Lineodds
        if (self.puck) and (type(bet) in [PassBet, LineOddsBet]):   # set the point for
            bet.point = self.puck                                   # pass, lineodds
        
        # Set the game_id
        if not bet.game_id:              # associates the bet with the game id
            bet.game_id = self.id        # so don't have to commit as often
            
        return bet
    
    
    @validates("rolls")
    def validate_rolls(self, key, roll):
        if not roll.game_id:              # rolls validator runs on append events
            roll.game_id = self.id        # associates the roll with the game
        return roll
        
          
    def roll(self, override=None):
        """
        :METHOD 
            craps.models.Game.roll(override=None)
        
        :INPUTS
            override = None or craps.models.Roll class
        """
         
        # Log the working bets
        self.log.info('[Table] ' + 'The shooter is ready...')
        self.log.info('[Table] ' +  'The point is {}'.format(self.puck or 'off'))
        for bet in self.working_bets:
            self.log.info('[Working] ' + bet.call_out())
        
        # Add a role      
        roll = override or Roll()                # @validates("rolls") associates  
        self.rolls.append(roll)                  # the roll with this game
        db_session.commit()                      # Commit to database
        
        # Call it out 
        self.log.info('[Roll] ' + (roll.call_out() or 'No action on {}'.format(roll.result)))
        
        # Evaluate bets
        self.evaluate_bets()
        db_session.commit() 
        
        # Count up the rail
        self.log.info('[Rail] ' + "You have {} on the rail".format(self.rail_balance))
        
        # Set the puck
        if (not self.puck) and (roll.result in [4,5,6,8,9,10]):            
            self.puck = roll.result            # Turn the puck on
                    
        elif (not self.puck) and (roll.result in [2,3,7,11,12]):
            self.puck = None                   # Craps or PassLine Winner. Keep the puck off
        
        elif (self.puck) and (roll.result == 7):
            self.puck = None                   # 7 out. Take the puck off
        
        elif (self.puck) and (roll.result == self.puck):
            self.puck = None                   # Winner. Take the puck off
                  
        # Commit the game after each roll
        db_session.commit()
            
    
    def bet(self, bet):
        """
        :METHOD 
            craps.models.Game.bet(bet)
        
        :INPUTS
            bet = craps.models.bet class
        
        :EXAMPLE
            Game.bet(PassBet(10))
        """
        
        # Append the bet   
        self.bets.append(bet)  # Validator will assign game_id and point

        # Commit the bet
        db_session.commit()
        
        # Logs
        self.log.info('[Bet] ' + 'You made a {} on {} for {}'.format(bet.type, bet.point or 'the box', bet.amount))
        self.log.info('[Rail] ' + "You have {} on the rail".format(self.rail_balance))
      
     
    def evaluate_bets(self):                # evaluate working bets
        for bet in self.working_bets:
            bet.evaluate()
    
    
    @hybrid_property
    def last_roll(self):                    # get the last roll 
        return self.rolls[-1]               # note to self... go back and make sure ordering is handled correctly
    
    @hybrid_property
    def working_bets(self):                 # get collection of working bets
        return db_session.query(Bet). \
                filter(Bet.game == self). \
                filter(Bet.working).all()

    @hybrid_property
    def unsettled_bets(self):                 # get collection of unsettled
        return db_session.query(Bet). \
                filter(Bet.game == self). \
                filter(Bet.settled == None).all()
                
    @hybrid_property
    def payouts(self):
        return db_session.query(func.sum(Bet.payout)). \
                filter(Bet.game == self).scalar() or 0
    
    @hybrid_property
    def total_amounts_bet(self):            # how much have I spent on bets this game?
        return db_session.query(func.sum(Bet.amount)). \
                filter(Bet.game == self).scalar() or 0
    
    @hybrid_property
    def total_amounts_working(self):        # how much do i have on the table?
        return db_session.query(func.sum(Bet.amount)). \
                filter(Bet.game == self). \
                filter(Bet.working == True).scalar() or 0

    @hybrid_property
    def bankroll(self):            # My realized gain or loss
        return self.payouts - self.total_amounts_bet
    
    @hybrid_property
    def rail_balance(self):        # My realized gain or loss
        return self.arrival_cash + self.bankroll

    
class Roll(Base):
   
    __tablename__ = 'rolls'
    
    id      = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(Integer, ForeignKey('games._id', onupdate="CASCADE", ondelete="CASCADE"))
    puck    = Column(Integer)
    die_one = Column(Integer)
    die_two = Column(Integer)
    
    game = relationship("Game")
    
    def __init__(self, override=(None, None)):
        
        self.die_one   = override[0] or pd.np.random.randint(1,7)
        self.die_two   = override[1] or pd.np.random.randint(1,7)
 
              
    @hybrid_property
    def result(self):
        return self.die_one + self.die_two


    def call_out(self):
        
        self.game.log.info('[Roll] ' + "Shooter rolled {}".format(self.result))
        self.puck = self.game.puck
             
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
            return "Craps. Take the line. Come again."
        
        # Craps Backup, pay the field
        if (self.result in [2, 12]):
            return "{} double the field".format(self.result)
        
        # Field Backup, pay the field
        if (self.result in [3, 4, 9, 10, 11]):
            return "{} pay the field".format(self.result)

        # 6 8 backup
        if (self.result in [6, 8]):
            return "{} {}".format(self.result, 
                    'the hard way' if self.die_one==self.die_two else 'came easy')
        
        # 5 backup
        if (self.result == 5):
            return "No field 5"


class Bet(Base):
    
    __tablename__ = 'bets'
    
    id      = Column(Integer, primary_key=True)
    type    = Column(String(50))
    game_id = Column(Integer, ForeignKey('games._id', onupdate="CASCADE", ondelete="CASCADE"))
    amount  = Column(Integer, nullable=False)
    point   = Column(Integer, default=None)
    working = Column(Boolean, default=True, nullable=False)
    payout  = Column(Integer, default=None)
    settled = Column(Integer, default=None)

    game = relationship("Game")    

    __mapper_args__ = {
        'polymorphic_identity':'bet',
        'polymorphic_on':type}

    def __init__(self, amount, point=None):
        
        self.amount = amount
        self.point  = point
        
        
    @validates('payout')
    def validate_payout(self, key, value):
        self.settled = self.game.last_roll.id
        self.working = False
        return value  

    
    def evaluate(self):
        
        # Log the payout amount
        if self.payout is not None:
            self.game.log.info('[Payout] ' + '{} {} {}'.format(self.type,
                'paid out' if self.payout > 0 else 'lost', 
                self.payout if self.payout > 0 else self.amount))
        
    
    def call_out(self):
        return '{t} for {a} is {w} on {p}'.format(t=self.type, a=self.amount, 
                w=('working' if self.working else 'not working'), p=self.point or 'the box')


class PassBet(Bet):
    
    __mapper_args__ = {
        'polymorphic_identity':'passbet'}
    
    def __init__(self, *args, **kwargs):
        super(PassBet, self).__init__(*args, **kwargs)

 
    def evaluate(self):
        
        roll       = self.game.last_roll  
               
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
    
    __mapper_args__ = {
    'polymorphic_identity':'comebet'}
    
    def __init__(self, *args, **kwargs):
        super(ComeBet, self).__init__(*args, **kwargs)

    def evaluate(self):
        
        roll = self.game.last_roll
                          
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
            self.game.log.info('[Bet] '+ "{t} for {a} was moved to the {r}".format(
                    t=self.type, a=self.amount, r=roll.result))
            

        # Log the result
        super(ComeBet, self).evaluate()
    

class LineOddsBet(Bet):
    
    __mapper_args__ = {
        'polymorphic_identity':'lineoddsbet'}
    
    def evaluate(self):
        
        # Validate working
        self.point   = self.game.puck          # Point is always the game puck
        self.working = self.point is not None  # If point is set it it working
        if not self.working:                   # Dont go to payouts if not working
            return
        
        roll       = self.game.last_roll
               
        # Payouts
        if (roll.result == self.point):      # Winner!
            self.payout = self.amount + self.amount * \
                {4:  2/1, 5: 3/2, 6: 6/5, 10: 2/1, 9: 3/2, 8: 6/5}[roll.result]      
        
        elif (roll.result == 7):
            self.payout = 0                   # 7 Out
        
        # Log the result
        super(LineOddsBet, self).evaluate()


class PointOddsBet(LineOddsBet):  

    __mapper_args__ = {
    'polymorphic_identity':'pointoddsbet'}
    
    
    def __init__(self, amount, point):
        super(PointOddsBet, self).__init__(amount, point)
    
    
    def evaluate(self):
        
        # Validate working
        self.working = self.game.puck is not None  # If point is set it is working
        
        roll       = self.game.last_roll
               
        # Payouts
        if (self.working) and (roll.result == self.point):  # Winner!
            self.payout = self.amount + self.amount * \
                {4:  2/1, 5: 3/2, 6: 6/5, 10: 2/1, 9: 3/2, 8: 6/5}[roll.result]     
        
        elif (self.working) and (roll.result == 7):         # 7 Out
            self.payout = 0                
        
        elif (not self.working) and (roll.result == 7):     # 7 on a comeout roll, push
            self.payout = self.amount              
        
        # Log the result
        super(LineOddsBet, self).evaluate()


class Simulation(Base):
    
    __tablename__ = 'simulations'
    
    id              = Column(Integer, primary_key=True, autoincrement=True)
    num_of_games    = Column(Integer, default=100)
    rolls_per_game  = Column(Integer, default=100)
    bet_unit        = Column(Integer, default=10)    
    description     = Column(Text,    default=None)
    
    games = relationship("Game", cascade="all, delete-orphan")
    
            
    def analyze(self):
        
        # qry rolls
        qry = db_session.query(Roll).join(Roll.game).filter(Game.simulation==self)
        rolls = pd.read_sql(qry.statement, qry.session.bind)
        
        # qry bets
        qry = db_session.query(Bet).join(Bet.game).filter(Game.simulation==self)
        bets = pd.read_sql(qry.statement, qry.session.bind)
        
        # Merge and Cash flow
        df = rolls.merge(bets, how='left', left_on=['id', 'game_id'], 
                         right_on=['settled', 'game_id']) # cost of unsettled bets are ignored due to left join
        df['cf'] = df['payout'] - df['amount']
        
        gb = df.groupby(['game_id'])['cf'].sum()
        
        # Stats
        self.avg  = gb.mean().round(2) # Average game sum of cashflow
        self.max  = gb.max().round(2)  # max game sum of cashflow
        self.min  = gb.min().round(2)  # Min game sum of cashflow
        self.std  = gb.std().round(2)  # Stdev of cash flows
        self.skew = gb.skew().round(2) # Skew
        self.kurt = gb.kurt().round(2) # Kurtosis
        
        self.prob_of_bankrupt = gb[gb==-200].count() / gb.count()
        self.prob_of_loss     = gb[gb < 0].count() / gb.count()
        self.prob_of_win      = gb[gb >= 0].count() / gb.count()
        
        self.df = df
        
        return self
    
    def plot_hist(self):
        ttl = 'avg: {}, std: {}, skew: {}, kurt: {}'.format(
                self.avg, self.std, self.skew, self.kurt)
        self.df.groupby(['game_id'])['cf'].sum().sort_values().plot.hist(title=ttl)
