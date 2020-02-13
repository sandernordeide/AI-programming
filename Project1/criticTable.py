class CriticTable:
    def __init__(self, alphaCritic, lambdod, gamma, criticValuation = 0, inputDim = 0, nodesInLayers = [0]):
        self.alphaCritic = alphaCritic
        self.lambdod = lambdod
        self.gamma = gamma
        self.surprise = 0
        self.stateValueEligibilities = {} #key, value is state, eligibility
        self.values = {}

    def createStateValues(self, state):
        if self.values.get(state) == None:
            self.values[state] = 0

    def findTDError(self, reinforcement, lastState, state):
        self.surprise = reinforcement + self.gamma*self.values[state] - self.values[lastState]
        return self.surprise

    def getTDError(self):
        return self.surprise

    def updateStateValues(self):
        alpha = self.alphaCritic
        surprise = self.surprise
        for state in self.values:
            e_s =self.stateValueEligibilities[state]
            self.values[state] = self.values[state] + alpha*surprise*e_s

    def createEligibility(self, state):
        if self.stateValueEligibilities.get(state) == None:
            self.stateValueEligibilities[state] = 0

    def updateCurrentEligibility(self, lastState):
        self.stateValueEligibilities[lastState] = 1

    def updateEligibilities(self):
        gamma =self.gamma
        lambdod = self.lambdod
        for state in self.stateValueEligibilities:
            self.stateValueEligibilities[state] = gamma*lambdod*self.stateValueEligibilities[state]
