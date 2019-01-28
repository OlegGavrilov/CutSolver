#!python3

from itertools import permutations
from typing import Collection, Tuple, List, Iterator


class TargetSize:
    def __init__(self, length: int, amount: int):
        self.length = length
        self.amount = amount

    def __lt__(self, other):
        return self.length < other.length

    def __str__(self):
        return f"l:{self.length}, n:{self.amount}"


class Job:
    # TODO: make this persistent across restarts to prevent collisions
    current_id = 0

    def __init__(self, length_stock: int, target_sizes: Collection[TargetSize], cut_width: int = 0):
        self._id = Job.current_id
        Job.current_id += 1

        self.length_stock = length_stock
        self.target_sizes = target_sizes
        self.cut_width = cut_width

    # utility

    def get_ID(self):
        return self._id

    def get_sizes(self) -> Iterator[int]:
        # generator, yield all lengths
        for size in self.target_sizes:
            for i in range(size.amount):
                yield size.length

    def __eq__(self, other):
        """
        Equality by ID, not by values
        """
        return self._id == other.get_ID()

    def __len__(self):
        """
        Number of target sizes in job
        """
        return sum(target.amount for target in self.target_sizes)


class Solver:
    # backend parameter
    n_max_precise = 20  # max 5sec per calculation
    n_max = 1000        # unreasonable time TODO might use timer instead

    @staticmethod
    def distribute(job: Job) -> Tuple[Collection[Collection[int]], int]:

        if len(job.target_sizes) < Solver.n_max_precise:
            return Solver._solve_bruteforce(job)
        elif len(job.target_sizes) < Solver.n_max:
            return Solver._solve_gapfill(job)
        else:
            raise OverflowError("Input too large")

    # CPU-bound
    # O(n!)
    @staticmethod
    def _solve_bruteforce(job: Job) -> Tuple[Collection[Collection[int]], int]:

        # find every possible ordering (n! elements)
        all_orderings = permutations(job.get_sizes())
        # TODO: remove duplicates

        # "infinity"
        min_trimmings = len(job) * job.length_stock
        min_stocks: List[List[int]] = []

        # TODO: Distribute combinations to multiprocessing worker threads
        for combination in all_orderings:
            stocks, trimmings = Solver._split_combination(combination, job.length_stock, job.cut_width)
            if trimmings < min_trimmings:
                min_stocks = stocks
                min_trimmings = trimmings

        return min_stocks, min_trimmings

    @staticmethod
    def _split_combination(combination: Tuple[int], length_stock: int, cut_width: int):
        """
        Collects sizes until length is reached, then starts another stock
        :param combination:
        :param length_stock:
        :param cut_width:
        :return:
        """
        stocks: List[List[int]] = []
        trimmings = 0

        current_size = 0
        current_stock: List[int] = []
        for size in combination:
            # fits into current
            if (current_size + size + cut_width) < length_stock:
                current_size += (size + cut_width)
                current_stock.append(size)
            else:
                # next stock
                stocks.append(current_stock)
                trimmings += Solver._get_trimming(length_stock, current_stock, cut_width)
                current_size = 0
                current_stock: List[int] = []
        if current_stock:
            stocks.append(current_stock)
            trimmings += Solver._get_trimming(length_stock, current_stock, cut_width)
        return stocks, trimmings

    # TODO: check if time varies with len(TargetSize) or TargetSize.amount
    # O(n^2)
    @staticmethod
    def _solve_gapfill(job: Job) -> Tuple[Collection[Collection[int]], int]:
        # input

        # TODO:
        # 1. Sort by magnitude (largest first)
        # 2. stack until limit is reached
        # 3. try smaller as long as possible
        # 4. create new bar

        targets = sorted(job.target_sizes, reverse=True)

        stocks = []
        trimming = 0

        current_size = 0
        current_stock = []

        i_target = 0
        while len(targets) > 0:

            # nothing fit, next stock
            if i_target >= len(targets):
                # add local result
                stocks.append(current_stock)
                trimming += Solver._get_trimming(job.length_stock, current_stock, job.cut_width)

                # reset
                current_stock = []
                current_size = 0
                i_target = 0

            current_target = targets[i_target]
            # target fits inside current stock, transfer to results
            if (current_size + current_target.length + job.cut_width) < job.length_stock:
                current_stock.append(current_target.length)
                current_size += current_target.length + job.cut_width

                # remove empty entries
                if current_target.amount <= 1:
                    targets.remove(current_target)
                else:
                    current_target.amount -= 1
            # try smaller
            else:
                i_target += 1

        # apply last "forgotten" stock
        if current_stock:
            stocks.append(current_stock)
            trimming += Solver._get_trimming(job.length_stock, current_stock, job.cut_width)

        # trimming could be calculated from len(stocks) * length - sum(stocks)
        return stocks, trimming

    # O(n)
    @staticmethod
    def _solve_FFD(job: Job) -> Tuple[Collection[Collection[int]], int]:
        # iterate over list of stocks
        # put into first stock that it fits into
        pass


    @staticmethod
    def _get_trimming(length_stock: int, lengths: Collection[int], cut_width: int) -> int:
        sum_lengths = sum(lengths)
        sum_cuts = len(lengths) * cut_width

        trimmings = length_stock - (sum_lengths + sum_cuts)

        if trimmings < 0:
            raise OverflowError

        return trimmings
