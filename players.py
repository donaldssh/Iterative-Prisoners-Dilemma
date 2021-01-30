import numpy as np
from abc import ABC, abstractmethod

class Player(ABC):
    """Abstract class, declare the move method"""
    @abstractmethod
    def move(self):
        pass 

class NiceGuy(Player):
    """
    Player that always outputs the cooperate move
    """
    def __init__(self, r_history=[], move_history=[]):
        self.r_history = r_history
        self.move_history = move_history
        self.label = "NiceGuy"
        
    def append_reward(self, reward):
        self.r_history.append(reward)
        
    def move(self):
        uc = [1,0]
        self.move_history.append(uc)
        return uc
    
    def p_reset(self):
        self.r_history = []
        self.move_history = []

    
class BadGuy(Player):
    """
    Player that always outputs the defect move
    """
    def __init__(self, r_history=[], move_history=[]):
        self.r_history = r_history
        self.move_history = move_history
        self.label = "BadGuy"
        
    def append_reward(self, reward):
        self.r_history.append(reward)
        
    def move(self):
        ud = [0,1]
        self.move_history.append(ud)
        return ud
    
    def p_reset(self):
        self.r_history = []
        self.move_history = []

    
class KBadGuy(Player):
    """
    Player that outputs the defect move 
    with probability k/100
    """
    def __init__(self, k, r_history=[], move_history=[]):
        self.k = k
        self.r_history = r_history
        self.move_history = move_history
        self.label = str(k) + "BadGuy"
        
    def append_reward(self, reward):
        self.r_history.append(reward)
        
    def move(self):
        uc = [1,0]
        ud = [0,1]
        if np.random.rand() > 1-(self.k/100):
            u = ud
        else:
            u = uc        
        self.move_history.append(u)
        return u
    
    def p_reset(self):
        self.r_history = []
        self.move_history = []
 
    
class Tit4Tat(Player):
    """
    Player, the first move is cooperate, 
    the subsequent moves are the same as the last 
    element in self.input_history
    """
    def __init__(self, r_history=[], move_history=[], input_history=[]):
        self.r_history = r_history
        self.move_history = move_history 
        self.input_history = input_history

    def append_reward(self, reward):
        self.r_history.append(reward)

    def append_input(self, inp):
        self.input_history.append(inp)

    def move(self):
        if len(self.input_history) == 0:
            u = [1,0]
        else:
            u = self.input_history[-1]
        self.move_history.append(u)
        return u
    
class Tit4TatMP(Player):
    """
    Player that starts with cooperate and then cooperates only if a fraction of players
    above or equal c_treshold has cooperated.
    """
    def __init__(self, r_history=[], move_history=[], input_history=[], c_threshold=0.5):
        self.r_history = r_history
        self.move_history = move_history 
        self.input_history = input_history
        self.c_threshold = c_threshold
        self.label = str(c_threshold) + "Tit4TatMP"
    
    def append_reward(self, reward):
        self.r_history.append(reward)
        
    def append_input(self, m_inp):
        """
        multiplayer input m_inp should be an array or list with N rows for N players,
        in every row the list [1,0] or [0,1], it also works with [1] or [0].
        The number of input players can change. 
        """
        self.input_history.append(m_inp)
        
    def move(self):
        if len(self.input_history) == 0:
            u = [1,0]
        else:
            last_inp = np.array(self.input_history[-1])[:,0]
            if np.sum(last_inp)/np.shape(last_inp)[0] >= self.c_threshold:
                u = [1,0]
            else:
                u = [0,1]
        self.move_history.append(u)
        return u
    
    def p_reset(self):
        self.r_history = []
        self.move_history = []
        self.input_history = []
        
        
class GrimTriggerMP(Player):
    """
    Player that cooperates until a numbers of players >= d_threshold defect in a turn,
    from now on he defects in every turn. 
    Setting d_threshold=0 means that it needs only one defecting player
    to start defecting itself.
    """
    def __init__(self, r_history=[], move_history=[], input_history=[], d_threshold=0.5):
        self.r_history = r_history
        self.move_history = move_history 
        self.input_history = input_history
        self.d_threshold = d_threshold
        self.defected = False
        self.label = "GrimTriggerMP"
    
    def append_reward(self, reward):
        self.r_history.append(reward)  
        
    def append_input(self, m_inp):
        """
        multiplayer input m_inp should be an array or list with N rows for N players,
        in every row the list [1,0] or [0,1], it also works with [1] or [0].
        The number of input players can change. 
        """
        self.input_history.append(m_inp)
    
    def move(self):  
        if not self.defected and len(self.input_history) > 0:
            # check if it has been defected in the last turn
            last_inp = last_inp = np.array(self.input_history[-1])[:,0]
            if np.sum(last_inp)/np.shape(last_inp)[0] < 1 - self.d_threshold:
                self.defected = True
#                 print("debug DEFECTED")
                
        if not self.defected:
            u = [1,0]
        else:
            u = [0,1]
        self.move_history.append(u)
        return u
    
    def p_reset(self):
        self.r_history = []
        self.move_history = []
        self.input_history = []

    
    
class LookBackPlayer(Player):
    """
    Player that use past rewards in order to decide the next move.
    """
    def __init__(self, bias, r_history=[], move_history=[], delta = 1):
        """
        bias is added to the past rewards during the move decision
        if bias is in range [-3,0] it can change the behaviour of the player
        """
        self.r_history = r_history
        self.move_history = move_history 
        self.bias = bias
        self.delta = delta
        self.label = str(delta) + "LookBackPlayer"
    
    def append_reward(self, reward):
        self.r_history.append(reward)
    

    def move(self):       
        # random move if its the first move
        if len(self.r_history) == 0:
            if np.random.rand() >= 0.5:
                u = [1,0]
            else:
                u = [0,1]
        else:            
            move_cat_history = np.array(self.move_history)
            deltas = np.array([self.delta**i for i in range(len(move_cat_history))])
            deltas = np.hstack((deltas,deltas))
            r_cat_history = np.concatenate((np.array([self.r_history]).T,np.array([self.r_history]).T), axis=1)
            sum_cat_r = np.sum((r_cat_history + self.bias) * move_cat_history, axis=0)

            if sum_cat_r[0]>sum_cat_r[1]:
                # cooperate 
                u = [1,0]
            elif sum_cat_r[0]<sum_cat_r[1]:
                # defect 
                u = [0,1]
            else:
                # random choice if parity
                if np.random.rand() >= 0.5:
                    u = [1,0]
                else:
                    u = [0,1]
                
        self.move_history.append(u)
        return u
    
    def p_reset(self):
        self.r_history = []
        self.move_history = []
