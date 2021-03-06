import unittest

from linguist.base.scanner.re_utils import atom, cat, alt, k_closure
from linguist.base.scanner.scanner import *


class TestScanner(unittest.TestCase):
    def test_easy_scan(self):
        category_info = {1: CategoryInfo('if', -1),
                         2: CategoryInfo('id', -2)}
        nfa1 = cat([atom('i', -1), atom('f', 1)])
        w = alt([atom(x, 2) for x in 'aif'])
        nfa2 = cat([w, k_closure(w)])
        nfa = alt([nfa1, nfa2])
        scanner = scanner_builder(nfa, category_info)
        tokens = scanner.tokens('if')
        self.assertEqual(list(tokens), [(1, 'if'), (eof, '')])
        tokens = scanner.tokens('ia')
        self.assertEqual(list(tokens), [(2, 'ia'), (eof, '')])

    def test_scan(self):
        category_info = {0: CategoryInfo('register', 0),
                         1: CategoryInfo('if', -1),
                         2: CategoryInfo('id', -2),
                         3: CategoryInfo('blank', -3),
                         4: CategoryInfo('eq', -4)}

        d = alt(atom(str(i), 0) for i in range(10))
        nfa0 = cat([atom('r', -1), d, d])
        nfa1 = cat([atom('i', -1), atom('f', 1)])
        w = alt([atom(chr(x), 2) for x in range(ord('a'), ord('z') + 1)])
        nfa2 = cat([w, k_closure(w)])
        space = atom(' ', 3)
        nfa3 = cat([space, k_closure(space)])
        nfa4 = atom('=', 4)
        nfa = alt([nfa0, nfa1, nfa2, nfa3, nfa4])
        scanner = scanner_builder(nfa, category_info)
        tokens = scanner.tokens('if  var = r31')
        self.assertEqual(list(tokens),
                         [(1, 'if'),
                          (3, '  '),
                          (2, 'var'),
                          (3, ' '),
                          (4, '='),
                          (3, ' '),
                          (0, 'r31'),
                          (eof, '')])

    def test_skip(self):
        category_info = {0: CategoryInfo('register', 0),
                         1: CategoryInfo('if', -1),
                         2: CategoryInfo('id', -2),
                         3: CategoryInfo('blank', -3, 'skip'),
                         4: CategoryInfo('eq', -4)}

        d = alt(atom(str(i), 0) for i in range(10))
        nfa0 = cat([atom('r', -1), d, d])
        nfa1 = cat([atom('i', -1), atom('f', 1)])
        w = alt([atom(chr(x), 2) for x in range(ord('a'), ord('z') + 1)])
        nfa2 = cat([w, k_closure(w)])
        space = atom(' ', 3)
        nfa3 = cat([space, k_closure(space)])
        nfa4 = atom('=', 4)
        nfa = alt([nfa0, nfa1, nfa2, nfa3, nfa4])
        scanner = scanner_builder(nfa, category_info)
        tokens = scanner.tokens('if  var = r31')
        self.assertEqual(list(tokens),
                         [(1, 'if'),
                          (2, 'var'),
                          (4, '='),
                          (0, 'r31'),
                          (eof, '')])

    def test_action(self):
        category_info = {0: CategoryInfo('register', 0, lambda x: int(x[1:])),
                         1: CategoryInfo('if', -1),
                         2: CategoryInfo('id', -2),
                         3: CategoryInfo('blank', -3, 'skip'),
                         4: CategoryInfo('eq', -4)}

        d = alt(atom(str(i), 0) for i in range(10))
        nfa0 = cat([atom('r', -1), d, d])
        nfa1 = cat([atom('i', -1), atom('f', 1)])
        w = alt([atom(chr(x), 2) for x in range(ord('a'), ord('z') + 1)])
        nfa2 = cat([w, k_closure(w)])
        space = atom(' ', 3)
        nfa3 = cat([space, k_closure(space)])
        nfa4 = atom('=', 4)
        nfa = alt([nfa0, nfa1, nfa2, nfa3, nfa4])
        scanner = scanner_builder(nfa, category_info)
        tokens = scanner.tokens('if  var = r31')
        self.assertEqual(list(tokens),
                         [(1, 'if'),
                          (2, 'var'),
                          (4, '='),
                          (0, 31),
                          (eof, '')])


if __name__ == '__main__':
    unittest.main()
