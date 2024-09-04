# Name: test_pa2.py
# Author: Dr. Glick
# Date: July 1, 2021
# Description: Tests pa2 for comp 370, fall 2021

import pa1
import pa2


def read_results_file(filename):
    file = open(filename)
    return [True if result == "Accept" else False for result in file.read().split()]


def dfa_file_format_ok(nfa, dfa_filename, nfa_filename):
    try:
        dfa_f = open(dfa_filename, "r")
        nfa_f = open(dfa_filename, "r")

        # Get num states in dfa
        num_states_dfa = int(dfa_f.readline().strip())
        states_list_dfa = list(range(1, num_states_dfa + 1))
        nfa_f.readline()  # skip over num states in nfa

        # Check that dfa alphabet is correct
        dfa_alphabet = dfa_f.readline().rstrip("\n")
        nfa_alphabet = nfa_f.readline().rstrip("\n")
        if set(dfa_alphabet) != set(nfa_alphabet):
            print("  DFA alphabet does not match NFA")
            return False

        # Check the dfa transition function
        try:
            dfa_transition_function_check = {
                (state, symbol): False
                for state in states_list_dfa
                for symbol in dfa_alphabet
            }
            for i in range(num_states_dfa * len(dfa_alphabet)):
                transition_function_entry = dfa_f.readline()
                tokens = transition_function_entry.split("'")
                from_state = int(tokens[0].strip())
                symbol = tokens[1]
                to_state = int(tokens[2].strip())
                if (
                    len(tokens) != 3
                    or from_state not in states_list_dfa
                    or symbol not in dfa_alphabet
                    or to_state not in states_list_dfa
                ):
                    print("  Invalid transition function entry in DFA file")
                    return False
                else:
                    dfa_transition_function_check[(from_state, symbol)] = True
        except ValueError:
            print("  Invalid DFA file.  Invalid state id in transition fucntion entry")
            return False
        if False in dfa_transition_function_check.values():
            print("  Invalid DFA file.  Transition function not complete")

        # Check start state
        try:
            start_state = int(dfa_f.readline().strip())
            if start_state not in states_list_dfa:
                raise ValueError
        except ValueError:
            print("DFA start state invalid")
            return False

        # Check accept states
        try:
            accept_states_str = dfa_f.readline().split()
            valid_accept_states = [
                True if int(x) in states_list_dfa else False for x in accept_states_str
            ]
            if False in valid_accept_states:
                raise ValueError
        except ValueError:
            print("DFA accept states invalid")
            return False

        dfa_f.close()
        return True
    except OSError:
        print("Could not open DFA file")
        return False


if __name__ == "__main__":
    num_test_files = 14
    for i in range(1, num_test_files + 1):
        nfa_filename = f"nfa{i}.txt"
        dfa_filename = f"dfa{i}.txt"
        input_filename = f"str{i}.txt"
        correct_results_filename = f"correct{i}.txt"

        print(f"Testing NFA {nfa_filename} on strings from {input_filename}")
        try:
            # Create NFA
            nfa = pa2.NFA(nfa_filename)

            # Convert to DFA
            nfa.toDFA(dfa_filename)

            # Check the format of the DFA file
            if not dfa_file_format_ok(nfa, dfa_filename, nfa_filename):
                print("  DFA file has incorrect formot")
            else:
                # Create the DFA
                dfa = pa1.DFA(dfa_filename)

                # Open string file.
                string_file = open(input_filename)

                # Simulate DFA on test strings
                results = []
                for str in string_file:
                    results.append(dfa.simulate(str.strip()))

                # Get correct results
                correct_results = read_results_file(correct_results_filename)

                # Check if correct
                if results == correct_results:
                    print("  Correct results")
                else:
                    print("  Incorrect results")
                    print(f"  Your results = {results}")
                    print(f"  Correct results = {correct_results}")
                print()
        except OSError as err:
            print(f"Could not open file: {err}")
        # except Exception as err:
        #    print(f"Error simulating dfa: {err}")
