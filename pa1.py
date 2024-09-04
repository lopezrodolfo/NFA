# Name: pa1.py
# Author: Rodolfo Lopez
# Date: 09/30/2021
# Description: DFA simulation

import re


class DFA:
    """Simulates a DFA"""

    # class variable used to recognize transition pattern from file
    trans_reg_exp = re.compile("\d* '.' \d*")

    def __init__(self, filename):
        """
        Initializes DFA from the file whose name is
        filename
        """

        # open infile
        self.filename = open(filename, "r")

        # read number of states (not necessary)
        self.num_states = int(self.filename.readline().rstrip())

        # read alphabet into list
        self.alpha = list(self.filename.readline().rstrip())

        # reads transition function into 2D list of str lists
        self.trans_func_list = []
        self.line = self.filename.readline()
        while DFA.trans_reg_exp.match(self.line):
            self.token = self.line.split()  # str list
            # token[0] = current state, token[1][1] = scanned symbol, token[2] = next state
            self.trans_func_list.append(
                [self.token[0], self.token[1][1], self.token[2]]
            )
            # on last iteration read start state
            self.start_state = self.line = self.filename.readline().rstrip()

        # read accept states into list
        self.accept_states = self.filename.readline().split()

        # close infile
        self.filename.close()

        # before simulation
        self.next_state = None
        self.final_state = None

    def simulate(self, str):
        """
        Simulates the DFA on input str.  Returns
        True if str is in the language of the DFA,
        and False if not.
        """
        # start of simulation
        self.num_transitions = 0

        # empty string case
        if str == "" and self.start_state in self.accept_states:
            return True

        for sym in str:
            if sym not in self.alpha:
                return False
            else:
                # pass start state initially to transition func
                if self.num_transitions == 0:
                    self.transition(self.start_state, sym)
                # pass next state to transition func
                else:
                    self.transition(self.next_state, sym)

        # after all symbols are read set final state
        self.final_state = self.next_state

        # accepting final state
        if self.final_state in self.accept_states:
            return True
        else:
            # rejecting final state
            return False

    def transition(self, cur_state, sym):
        # increment transition
        self.num_transitions += 1
        for trans in self.trans_func_list:
            # current state matches with current symbol
            if (trans[0] == cur_state) and (trans[1] == sym):
                self.next_state = trans[2]  # go to next state
