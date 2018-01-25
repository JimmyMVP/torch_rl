import numpy as np
import gym
from gym import spaces
from gym.utils import seeding

class BitFlippingEnv(object):


    def __init__(self, num_bits=10):
        self.num_bits = num_bits
        self.state = np.zeros(num_bits, dtype=np.uint8)
        # Maybe too hard?
        self.goal = np.random.choice([0,1], num_bits).astype(np.uint8)


    def step(self, action):
        if action < self.state.size:
            self.state[action] ^= 1
        self.done = np.array_equal(self.state, self.goal)

        return self.state, int(self.done), self.done, {}

    def reset(self):
        self.goal = np.random.choice([0,1], self.num_bits)
        self.state = np.zeros(self.num_bits, dtype=np.uint8)
        self.done = False

    def get_observation(self):
        return self.state

    def distance(self):
        return np.sum(np.abs(self.state-self.goal))




class NormalisedActions(gym.ActionWrapper):

    def _action(self, action):
        action = (action + 1) / 2  # [-1, 1] => [0, 1]
        action *= (self.action_space.high - self.action_space.low)
        action += self.action_space.low
        return action

    def _reverse_action(self, action):
        action -= self.action_space.low
        action /= (self.action_space.high - self.action_space.low)
        action = action * 2 - 1
        return action


class BanditEnv(gym.Env):

    def __init__(self, num_bandits):
        self.num_bandits=num_bandits
        self.viewer = None

        self.high = np.ones(num_bandits)
        self.action_space = spaces.Discrete(num_bandits)
        """
            The observations are rewards from all of the bandits
        """
        self.observation_space = spaces.Box(low=-self.high, high=self.high)

        self._seed()

        self.bandit_distributions = [self.np_random.uniform(0,1) for x in range(num_bandits)]


    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def _step(self,a):
        bandit_rewards = [self.np_random.choice([-1,1], p=[1-p, p]) for p in self.bandit_distributions]
        self.state = np.asarray(bandit_rewards)
        return self._get_obs(), bandit_rewards[a], False, {}

    def _reset(self):
        self.state = self.np_random.uniform(low=-self.high, high=self.high)
        return self.state

    def _get_obs(self):
        return self.state

