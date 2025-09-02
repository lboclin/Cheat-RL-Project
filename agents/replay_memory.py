import random
from collections import namedtuple, deque

# Define the structure of a single experience/transition using a namedtuple for readability.
Transition = namedtuple('Transition', 
                        ('state', 'action', 'next_state', 'reward', 'done'))

class ReplayMemory:
    """
    A cyclic buffer of bounded size that stores the transitions observed by the agent.
    This prevents the agent from only learning from its most recent experiences.
    """
    def __init__(self, capacity: int):
        """
        Initializes the memory.

        Args:
            capacity (int): The maximum number of transitions to store.
        """
        # A deque is a double-ended queue, highly efficient for adding and removing
        # items. It automatically discards old entries when the max length is reached.
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Saves a transition to the memory."""
        self.memory.append(Transition(*args))

    def sample(self, batch_size: int) -> list:
        """
        Selects a random batch of transitions for training. This random sampling
        breaks the correlation between consecutive experiences, stabilizing the learning.
        """
        return random.sample(self.memory, batch_size)

    def __len__(self) -> int:
        """Allows calling len(memory) to get the current number of stored transitions."""
        return len(self.memory)