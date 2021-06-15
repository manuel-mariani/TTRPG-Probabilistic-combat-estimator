import numpy as np
import matplotlib.pyplot as plt


# ------------------------------------------- #
#  Dice model                                 #
# ------------------------------------------- #
class Dice:
    def __init__(self, times, die, mod=0, boons=0):
        assert times > 0 and die > 0

        self.distribution, self.values = Dice._distribution_values(times, die, mod, boons)
        self.pmf = self.distribution / sum(self.distribution)  # Probability mass function
        self.cdf = np.cumsum(self.pmf)  # Cumulative distribution function
        self.cardinality = len(self.values)
        self.avg = sum([self.values[i] * self.pmf[i] for i in range(self.cardinality)])

        # Stringify the dice
        s = f"{times}d{die}"
        if mod != 0:
            s += f"+{mod}" if mod > 0 else str(mod)
        s += f"@{boons}" if boons != 0 else ""
        self.string = s

    # ------------------------------------------- #

    @staticmethod
    def _distribution_values(times, die, mod, boons) -> (np.ndarray, np.ndarray):
        """ Returns a dice distribution based on a dice formula """
        # Define the bounds
        low_bound = mod + times
        upp_bound = mod + times * die

        # Determine the distribution of only the base dice
        dice = np.ones(die, dtype=int)
        dist = dice.copy()
        for i in range(1, times):
            dist = np.convolve(dist, dice)

        # Sum the boon distribution
        if boons != 0:
            # Extend bounds based on n boons
            if boons > 0:
                low_bound += 1
                upp_bound += 6
            else:
                low_bound -= 6
                upp_bound -= 1
            # Add the boons by convolution
            boon = Dice._boon_distribution(boons)
            dist = np.convolve(dist, boon)

        return dist, np.arange(low_bound, upp_bound + 1)

    # ------------------------------------------- #

    @staticmethod
    def _boon_distribution(n_boons, die=6) -> np.ndarray:
        """ Returns the probability distribution of n_boons d die keep highest"""
        cdf = np.cumsum(np.full(die, 1 / die))
        cdf = np.power(cdf, abs(n_boons))
        cdf[1:] -= cdf[:-1].copy()

        if n_boons < 0:
            return np.flip(cdf)
        return cdf

    # ------------------------------------------- #

    def prob_against(self, target: int) -> [float, float]:
        """ returns (probability of failure, probability of success) of dice against the target"""
        assert isinstance(target, int)

        # Check bounds
        low_bound, upp_bound = self.values[0], self.values[-1]
        if low_bound >= target:
            return [0, 1]
        if upp_bound < target:
            return [1, 0]

        fail_prob = self.cdf[target - low_bound - 1]
        # The -1 is there because if the result matches the target, it is a success
        succ_prob = 1 - fail_prob
        return [np.round(fail_prob, 2), np.round(succ_prob, 2)]

    # ------------------------------------------- #

    @staticmethod
    def combine(*dices):
        """ Combine multiple dice into one """
        # Bounds
        low_bound = min([d.values[0] for d in dices])
        upp_bound = max([d.values[-1] for d in dices])

        # Zero translations, for ensuring 0 is in the interval
        lb_zt = 0 if low_bound <= 0 else low_bound
        ub_zt = 0 if upp_bound >= 0 else upp_bound

        # Initialize the probabilities as zeros and the values as a linear range between the bounds
        values = np.arange(low_bound - lb_zt, upp_bound - ub_zt + 1)
        probab = np.zeros(len(values))

        # For each dice, sum the probabilities on the union of the two domains
        for d in dices:
            start_index = np.where(values == d.values[0])[0][0]
            stop_index = start_index + len(d.values)
            probab[start_index:stop_index] += d.pmf

        # Create the resulting dice
        tot = Dice(1, 1)
        tot.distribution = probab
        tot.pmf = probab / sum(probab)
        tot.values = values
        tot.cdf = np.cumsum(tot.pmf)
        tot.cardinality = len(values)
        tot.avg = sum([tot.values[i] * tot.pmf[i] for i in range(tot.cardinality)])
        tot.string = ' + '.join([str(d) for d in dices])
        return tot

    # ------------------------------------------- #

    def plot(self, title=None):
        if title is not None:
            plt.suptitle(title, fontsize=18)
        else:
            plt.suptitle(str(self), fontsize=18)
        plt.bar(self.values, self.distribution)
        plt.show()

    # ------------------------------------------- #

    def __str__(self):
        return self.string

    # ------------------------------------------- #
