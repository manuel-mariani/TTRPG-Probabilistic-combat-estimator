import numpy as np
from src.dice import Dice
import matplotlib.pyplot as plt


# ------------------------------------------- #
#  Aleatory Variable                          #
# ------------------------------------------- #
class AleatoryVariable:
    def __init__(self, domain: np.ndarray, distribution: np.ndarray):
        self.domain = domain
        self.distribution = distribution

    # ------------------------------------------- #

    @staticmethod
    def from_exact(value: int, bounds: (int, int) = None):
        """ Create an Aleatory Variable from an integer. @bounds determines the domain of the variable"""
        if bounds is None:
            return AleatoryVariable(domain=np.array([value]), distribution=np.ones(1))
        else:
            lb, ub = bounds
            domain = np.arange(lb, ub + 1)
            assert value in domain
            distribution = np.zeros(ub - lb + 1)
            distribution[domain == value] = 1
            return AleatoryVariable(domain, distribution)

    # ------------------------------------------- #

    @staticmethod
    def from_dice(dice: Dice):
        """ Create an Aleatory Variable from a Dice object"""
        return AleatoryVariable(domain=dice.values, distribution=dice.pmf)

    # ------------------------------------------- #

    @staticmethod
    def from_hit(dice: Dice, target: int):
        """ Create an Aleatory Variable using a Dice and a target [Dice(x >= target]"""
        domain = np.arange(0, 2)
        distribution = np.array(dice.prob_against(target))
        return AleatoryVariable(domain, distribution)

    # ------------------------------------------- #

    def set_domain_bounds(self, low_bound, upp_bound):
        """ Extends the domain of the aleatory variable"""
        assert low_bound <= self.domain[0] and upp_bound >= self.domain[-1]
        # If the new domain would be the same as the current, return
        if low_bound == self.domain[0] and upp_bound == self.domain[-1]:
            return

        # Define the new domain and initialize the distribution
        new_domain = np.arange(low_bound, upp_bound + 1)
        new_distribution = np.zeros(len(new_domain))

        # Copy the old distribution into the new, starting and ending at the extremities of the union of the two
        start_index = np.where(new_domain == self.domain[0])[0][0]
        stop_index = start_index + len(self.domain)
        new_distribution[start_index:stop_index] = self.distribution

        # Replace the domain and distribution
        self.domain = new_domain
        self.distribution = new_distribution

    # ------------------------------------------- #

    def __pow__(self, n):
        """
        Elevate the Aleatory Variable to an integer value
        n > 0
         performs n-1 convolutions on the distribution and extends the domain wrt the result of the convolutions.
        n < 0
         same case of n > 0, but the domain is flipped
        n = 0
         returns an aleatory variable centered in 0, with P(0) = 1
        """
        assert isinstance(n, int)
        if n == 0:
            return AleatoryVariable.from_exact(0)
        else:
            domain = np.arange(self.domain[0] * abs(n), self.domain[-1] * abs(n) + 1)
            distribution = self.distribution.copy()
            for t in range(abs(n) - 1):
                distribution = np.convolve(distribution, self.distribution)
            if n > 0:
                return AleatoryVariable(domain, distribution)
            return AleatoryVariable(np.flip(-domain), np.flip(distribution))

    # ------------------------------------------- #

    def __sub__(self, other):
        """ Subtracts an Aleatory Variable @other to the current. Inverse of __add__ """
        assert isinstance(other, AleatoryVariable)

        # Iterate through the length of the current variable. For each probability in the distribution do:
        distribution = np.zeros(len(self))
        for s in range(len(self)):
            # 1. Multiply it with the entire other distribution
            weighted_partial = other.distribution * self.distribution[s]

            # 2. Store the new weighted distribution, but with its domain "shifted" according to the two domains
            for o in range(len(weighted_partial)):
                index = s - other.domain[o]
                # Keep the distribution inside the current domain by adding it to the extrema
                if index < 0:
                    distribution[0] += weighted_partial[o]
                elif index >= len(self):
                    distribution[-1] += weighted_partial[o]
                else:
                    distribution[index] += weighted_partial[o]

        return AleatoryVariable(self.domain, distribution)

    # ------------------------------------------- #

    def __add__(self, other):
        """ Adds an Aleatory Variable @other to the current. Inverse of __sub__ """
        assert isinstance(other, AleatoryVariable)
        tmp = AleatoryVariable(other.domain * -1, other.distribution)
        return self - tmp

    # ------------------------------------------- #

    def __mul__(self, other):
        """
        Multiply an Aleatory Variable @other with the current. Despite the name, this operation is not commutative.
        """
        assert isinstance(other, AleatoryVariable)

        # Multiply the two domains to form the resulting
        low_bound = self.domain[0] * other.domain[0]
        upp_bound = self.domain[-1] * other.domain[-1]
        domain = np.arange(low_bound, upp_bound + 1)

        # Initialize a distribution and a variable
        distribution = np.zeros(len(domain))
        variable = AleatoryVariable(domain, distribution)

        # Iterate through the length of the other variable, performing:
        for o in range(len(other)):
            # 1. Elevate the current variable to a value of the other variable
            tmp = (self ** int(other.domain[o]))

            # 2. Weight the result of 1 (distribution) based on the probability of the other value
            tmp.distribution *= other.distribution[o]

            # 3. Sum the weighted distribution to the new distribution, shifted accordingly to the domain
            start_index = np.where(domain == tmp.domain[0])[0][0]
            stop_index = start_index + len(tmp)
            variable.distribution[start_index:stop_index] += tmp.distribution

        # Normalize the variable and return it
        variable.distribution /= sum(variable.distribution)
        return variable

    # ------------------------------------------- #

    def __len__(self):
        return len(self.domain)

    def __str__(self):
        pairs = list(zip(self.domain, np.around(self.distribution, 6)))
        return str(pairs)

    # ------------------------------------------- #

    def plot(self, title=None):
        if title is not None:
            plt.suptitle(title, fontsize=18)
        plt.bar(self.domain, self.distribution)
        plt.show()

    # ------------------------------------------- #


# ------------------------------------------- #
#  Example                                    #
# ------------------------------------------- #
if __name__ == '__main__':
    av1 = AleatoryVariable.from_dice(Dice(1, 20, 0, 3))
    av1.plot("$V_1$")

    av2 = AleatoryVariable.from_dice(Dice(1, 6))
    av2.plot("$V_2$")

    power_av2 = av2 ** 3
    power_av2.plot("$V_2^3$")
    AleatoryVariable.from_dice(Dice(3, 6)).plot("3d6")

    minus = av1 - av2
    minus.plot("$V_1 - V_2$")

    times = av1 * av2
    times.plot("$V_1 \\times V_2$")

    times = av2 * av1
    times.plot("$V_2 \\times V_1$")

