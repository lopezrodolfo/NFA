# Name: pa2.py
# Author: Rodolfo Lopez
# Date: 10/27/2021
# Description: NFA to DFA conversion

import re


class NFA:
    """Simulates an NFA"""

    # class variable used to recognize transition pattern from file
    trans_reg_exp = re.compile("\d* '.' \d*")

    def __init__(self, nfa_filename):
        """
        Initializes NFA from the file whose name is
        nfa_filename.  (So you should create an internal representation
        of the nfa.)
        """

        # open infile
        self.nfa_filename = open(nfa_filename, "r")

        # read number of states into int
        self.num_states_nfa = int(self.nfa_filename.readline().strip())

        # read alphabet into str
        self.alpha_nfa = self.nfa_filename.readline().strip()

        # invalid alphabet
        if "e" in self.alpha_nfa:
            print(
                'The NFA alphabet cannot contain the symbol "e" since it is used for epsilon transitons.'
            )

        # read transition function into 2D list of str lists
        self.trans_func_list_nfa = []
        self.line = self.nfa_filename.readline()
        while NFA.trans_reg_exp.match(self.line):  # while pattern matches transition
            self.token = self.line.split()  # str list
            # token[0] = current state, token[1][1] = scanned symbol, token[2] = next state
            self.trans_func_list_nfa.append(
                [self.token[0], self.token[1][1], self.token[2]]
            )
            # on last iteration read empty line
            self.empty_line = self.line = self.nfa_filename.readline().strip()

        # read start state into str
        self.start_state_nfa = self.nfa_filename.readline().strip()

        # read accept states into str list
        self.accept_states_nfa = self.nfa_filename.readline().strip().split()

        # close infile
        self.nfa_filename.close()

    def toDFA(self, dfa_filename):
        """
        Converts the "self" NFA into an equivalent DFA
        and writes it to the file whose name is dfa_filename.
        The format of the DFA file must have the same format
        as described in the first programming assignment (pa1).
        This file must be able to be opened and simulated by your
        pa1 program.

        This function should not read in the NFA file again.  It should
        create the DFA from the internal representation of the NFA that you
        created in __init__.
        """

        # DFA set of start states contains only the NFA start state
        self.start_states_set_dfa = set(self.start_state_nfa)
        # States reachable via epsilon transitions added to DFA set of start states
        self.start_states_set_dfa = self.generateEpsilonTransitions(
            self.start_states_set_dfa
        )  # ret hashable frozen set

        # {NFA state: DFA state} where NFA state is a immutable set and DFA state is an int
        self.state_dict_dfa = {}
        self.state_label_dfa = 1  # DFA state number
        self.state_dict_dfa[self.start_states_set_dfa] = (
            self.state_label_dfa
        )  # add start state

        # init cur state with no valid transitions for algoritim
        self.current_states_set_dfa = self.start_states_set_dfa

        # keeps track of states without valid transitions defined for each sym in alpha
        self.stack = []
        self.stack.append(self.current_states_set_dfa)

        self.trans_func_list_dfa = []  # DFA trans func will be written in output file
        self.converted = False  # no DFA yet
        while (
            not self.converted or len(self.stack) > 0
        ):  # scan NFA states until DFA is fully constructed (valid transitions in each state for each sym in alpha)
            self.converted = True
            self.current_states_set_dfa = set(
                self.stack.pop()
            )  # get DFA state without valid transition

            for (
                sym
            ) in (
                self.alpha_nfa
            ):  # define valid transition for each state for each symbol in alphabet
                self.next_states_set_dfa = set()  # no next state yet
                self.next_states_set_dfa = self.generateSymbolTransitions(
                    sym
                )  # ret list
                self.next_states_set_dfa = self.generateEpsilonTransitions(
                    self.next_states_set_dfa
                )  # ret frozen set

                if (
                    self.next_states_set_dfa in self.state_dict_dfa
                ):  # if DFA state already exists
                    self.trans_func_list_dfa.append(
                        [
                            self.state_dict_dfa[frozenset(self.current_states_set_dfa)],
                            sym,
                            self.state_dict_dfa[frozenset(self.next_states_set_dfa)],
                        ]
                    )  # no need to create a new DFA state simply add valid DFA trans
                else:  # DFA state does not exist
                    self.state_label_dfa += 1  # add new state value
                    self.state_dict_dfa[frozenset(self.next_states_set_dfa)] = (
                        self.state_label_dfa
                    )  # new DFA state is constructed

                    self.trans_func_list_dfa.append(
                        [
                            self.state_dict_dfa[frozenset(self.current_states_set_dfa)],
                            sym,
                            self.state_dict_dfa[frozenset(self.next_states_set_dfa)],
                        ]
                    )  # add valid DFA trans
                    self.stack.append(
                        self.next_states_set_dfa
                    )  # new DFA state added to states that need valid transitions defined
                    self.converted = (
                        False  # created a new DFA w/o any valid transitions defined
                    )

        self.outfile = open(dfa_filename, "w")  # open DFA outfile

        self.outfile.write(str(len(self.state_dict_dfa)) + "\n")  # write DFA num states

        self.outfile.write(self.alpha_nfa + "\n")  # write DFA alphabet

        for trans in self.trans_func_list_dfa:  # write DFA trans func
            self.outfile.write(
                str(trans[0]) + " '" + str(trans[1]) + "' " + str(trans[2]) + "\n"
            )

        self.outfile.write(str(1) + "\n")  # DFA start state always 1

        self.generateAcceptStates()  # void helper method to init DFA accept states

        for state in self.accept_states_set_dfa:  # write accept states
            self.outfile.write(str(state) + " ")

        self.outfile.write("\n")

        self.outfile.close()  # close outfile

    def generateEpsilonTransitions(self, states):
        """Returns frozen set of states that have epsilon transitions defined in the passed in states"""
        self.states_list_dfa = list(states)
        i = 0
        while i < len(self.states_list_dfa):
            for trans in self.trans_func_list_nfa:  # scan trans func list for NFA
                if (
                    trans[0] == self.states_list_dfa[i]
                    and trans[1] == "e"
                    and trans[2] not in self.states_list_dfa
                ):  # look for e trans
                    self.states_list_dfa.append(trans[2])  # add to DFA state set
                    i = -1  # new state added to state list may also have e trans
                    break
            i += 1
        return frozenset(sorted(set(self.states_list_dfa)))

    def generateSymbolTransitions(self, symbol):
        """Returns set of next states that have valid symbol trans defined for all states in the current set of states"""
        self.cur_states_list_dfa = list(self.current_states_set_dfa)

        for i in range(len(self.cur_states_list_dfa)):
            for trans in self.trans_func_list_nfa:  # scan trans func list for NFA
                if (
                    trans[0] == self.cur_states_list_dfa[i]
                    and trans[1] == symbol
                    and trans[2] not in self.next_states_set_dfa
                ):  # check if new state needed
                    self.next_states_set_dfa.add(trans[2])  # add new state

        return set(self.next_states_set_dfa)

    def generateAcceptStates(self):
        """Void method to init accept states"""
        self.accept_states_set_dfa = set()
        for state in self.state_dict_dfa:
            if (
                len(state.intersection(self.accept_states_nfa)) > 0
            ):  # state in DFA set of states has at least one state in set of NFA accept states
                self.accept_states_set_dfa.add(
                    self.state_dict_dfa[state]
                )  # add DFA state to set of DFA accepting states
