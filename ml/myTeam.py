# myTeam.py
# ---------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'DummyAgent', second = 'DummyAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on). 
    
    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    ''' 
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py. 
    '''
    CaptureAgent.registerInitialState(self, gameState)

    ''' 
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)

    ''' 
    You should change this in your own agent.
    '''

    return random.choice(actions)


class GeneticAgent(CaptureAgent):
  
  def __init__( self, index, timeForComputing = .1, weightList ):
    """
    Lists several variables you can query:
    self.index = index for this agent
    self.red = true if you're on the red team, false otherwise
    self.agentsOnTeam = a list of agent objects that make up your team
    self.distancer = distance calculator (contest code provides this)
    self.observationHistory = list of GameState objects that correspond
        to the sequential order of states that have occurred so far this game
    self.timeForComputing = an amount of time to give each turn for computing maze distances
        (part of the provided distance calculator)
    """
    # Agent index for querying state
    self.index = index

    # Whether or not you're on the red team
    self.red = None

    # Agent objects controlling you and your teammates
    self.agentsOnTeam = None

    # Maze distance calculator
    self.distancer = None

    # A history of observations
    self.observationHistory = []

    # Time to spend each turn on computing maze distances
    self.timeForComputing = timeForComputing

    # Access to the graphics
    self.display = None
    self.FoodHuntingWeight = weightList[1]
    self.ScoreWeight = weightList[2]
    self.PacmanHunterWeight = weightList[3]
    self.PreventingWeight = weightList[4]
    self.EatingGhost = weightList[5]
    self.RunningGhost = weightList[6]
    self.CapsuleWeight = weightList[7]
    self.CountDownWeight = weightList[8]
    self.BorderWeight = weightList[9]
    self.PathesWeight = weightList[10]
    self.SeperationWeight = weightList[11]
      
      
      
  def chooseAction(self, gameState):
      
      
      actions = gameState.getLegalActions(self.index)
      if actions:
          max = actions[0] 
          maxVal = self.evaluateActions(actions[0], gameState)
          for a in actions: 
              currentVal = self.evaluateAction(a, gameState)
              if  currentVal > maxVal: 
                  maxVal = currentVal
                  max = a
          return a
      return 

  def evaluateAction(self, action, gameState):
      successor = gameState.getSuccessorState(self.index, action)
      #score calculations
      score = successor.getScore()
      if self.red: 
          sum = score * self.ScoreWeight
      else 
          sum = -score * self.ScoreWeight
      #food calculations
      newFood = self.getFood(successor)
      spots = []
      foodDistances = []
      count = 0
      for f in newFood:
        c = 0
        for ff in f: 
            if newFood[count][c]:
                spots.append((count, c))
            c = c + 1
        count = count + 1
      for s in spots: 
          foodDistances.append(self.getMazeDistance(successor.getAgentState(self.index).getPosition(), s))
      sum = sum + (10/(min(foodDistances))) * self.FoodHuntingWeight
      #capsule calculations
      count = 0 
      newCapsules = self.getCapsules(successor) 
      cspots = []
      capsuleDistances = []
      for c in newCapsules:
          a = 0
          for cc in c: 
              if newCapsules[count][a]:
                   spots.append((count,a))
              a = a + 1
          count = count + 1
      sucPos=successor.getAgent(self.index).getPostion()
      for s in cspots: 
          capsuleDistances.append(self.getMazeDistance(sucPos, s))
      sum = sum + (10/(min(capsuleDistances))) *self.CapsuleWeight
      #food defending calculations
      enemyDistances=[]
      en=self.getOpponents(successor)
      tspots=[]
      tfood=self.getFoodYouAreDefending(successor)
      count=0
      for f in tfood:
        c = 0
        for ff in f: 
            if tfood[count][c]:
                tspots.append((count, c))
            c = c + 1
        count = count + 1
      enFoodCount=len(tspots)
      sum = sum + (enFoodCount * self.CountDownWeight)
      for x in en:
        tempSpots=[]
        enemyDistances.append(self.getMazeDistance(sucPos,successor.getAgentPosition(x)))
        for z in tspots:
          tempSpots.append(self.getMazeDistance(z, successor.getAgentPosition(x)))
        tspots.append(min(tempspots))
      enemyDistToDot=min(tspots)
      sum = sum + enemyDistToDot * self.PreventingWeight
      #seperation calculations
      team=self.getTeam()
      teamDistance=self.getMazeDistance(successor.getAgentPosition(team[0]),successor.getAgentPosition(team[1]))
      sum = sum + teamDistance
      #pathes calculation
      numMoves=len(successor(getLegalActions(self.index)))
      sum = sum + numMoves * self.PathesWeight
      #fleeing and attacking ghosts
      minEnemyDistance = min(enemyDistances)
      attack = 0
      flee = 0
      opponents = self.getOpponents(successor)
      
      if successor.agentStates[opponents[0].index].scaredTimer != 0 or successor.agentStates[opponents[1].index].scaredTimer != 0: 
        attack = 10/minEnemyDistance
      else 
        flee = minEnemyDistance
      sum = sum + (attack * self.EatingGhost) + (flee * self.RuningGhost)
      #border calculations  
      borderDist=abs(sucPos[0]-len(successor.getwalls()[0])/2)
      sum = sum + borderDist * self.BorderWeight
      op1d = self.getMazeDistance(successor.getAgentPosition(self.index), successor.getAgentPosition(opponents[0].index))
      op2d = self.getMazeDistance(successor.getAgentPosition(self.index), successor.getAgentPosition(opponents[1].index)) 
      if  op1d > op2d :
          if self.getAgentStates(opponents[1].index).isPacman:
              sum = sum + 10/(op1d * self.PacmanHunterWeight)
      else: 
          if self.getAgentStates(opponents[0].index).isPacman: 
              sum = sum + 10/(op2d * self.PacmanHunterWeight)
          
      
          
        
        
        
        