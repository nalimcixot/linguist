from collections import defaultdict

from linguist.base.scanner.dfa import DFA

from linguist.base.scanner.nfa_to_dfa import dict_to_dfa_matrix


class RevIndex:
    def __init__(self, partitions):
        self.p_map = {}
        self.p_id = 0
        for partition in partitions:
            for state in partition:
                self.p_map[state] = self.p_id
            self.p_id += 1

    def find_part(self, state):
        if state is None:
            return -1
        else:
            return self.p_map[state]

    def mark_new_part(self, states):
        for state in states:
            self.p_map[state] = self.p_id
        self.p_id += 1


def split(dfa, rev_index, partition):
    states = set(partition)
    sample = states.pop()
    first_set = {sample}
    second_set = set()
    while states:
        state = states.pop()
        for char in dfa.alphabet:
            if rev_index.find_part(dfa.trans_matrix[sample][char]) \
                    != rev_index.find_part(dfa.trans_matrix[state][char]):
                second_set.add(state)  # char distinguishes this state
                break
        else:
            first_set.add(state)  # no char distinguishes this state

    if second_set:  # partition split
        rev_index.mark_new_part(second_set)
        return {frozenset(first_set), frozenset(second_set)}
    else:
        return {frozenset(first_set)}


def partition_acc_states(acc_states):
    rev_map = defaultdict(set)
    for state, category in acc_states.items():
        rev_map[category].add(state)
    return frozenset(frozenset(x) for x in rev_map.values())


def partition_states(dfa):
    partitions = set()
    new_partitions = partition_acc_states(dfa.accepting_states)
    non_acc_states = frozenset(set(dfa.trans_matrix.keys()) - set(dfa.accepting_states.keys()))
    if non_acc_states:
        new_partitions |= {non_acc_states}
    rev_index = RevIndex(new_partitions)
    while new_partitions != partitions:
        partitions = new_partitions
        new_partitions = set()
        for partition in partitions:
            new_partitions |= split(dfa, rev_index, partition)
    return partitions, rev_index


def minimize_dfa(dfa):
    _, rev_index = partition_states(dfa)

    # build the transition matrix
    trans_matrix = {}
    for start, v in dfa.trans_matrix.items():
        trans_matrix[rev_index.find_part(start)] = {}
        for char, end in v.items():
            if end is not None:
                trans_matrix[rev_index.find_part(start)][char] = rev_index.find_part(end)
    new_matrix = dict_to_dfa_matrix(trans_matrix)

    # build the starting state
    starting_state = rev_index.find_part(dfa.starting_state)

    # build accepting states
    accepting_states = {}
    for state in dfa.accepting_states:
        accepting_states[rev_index.find_part(state)] = set()
    for state in dfa.accepting_states:
        accepting_states[rev_index.find_part(state)] = dfa.accepting_states[state]

    return DFA(new_matrix,
               starting_state,
               accepting_states,
               dfa.alphabet,
               dfa.classifier)
