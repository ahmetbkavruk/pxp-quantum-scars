"""Basis-state operations and PXP Hamiltonian construction.

The initial refactor preserves the exact representation and periodic-boundary
conventions from the original research notebook.
"""

from scipy.sparse import csr_matrix


class basisStates:
    def __init__(self, L):
        self.L = L
        self.dim = 2**L

    def state(self, index):
        return format(index, f"0{self.L}b")

    def getIndex(self, state):
        return int(state, 2)
    
    def getAllBasisStates(self):
        return [self.state(i) for i in range(self.dim)]
    
    def x(self, index, site):
        if index is None:
            return None

        operated_state = self.state(index)

        flipped_bit = str(1 - int(operated_state[site]))

        new_state = operated_state[:site] + flipped_bit + operated_state[site+1:]
        
        return self.getIndex(new_state)
    
    def p(self, index, site):
        if index is None:
            return None

        operated_state = self.state(index)
    
        if operated_state[site] == '1':
            return None
        else:
            return index

    def pxp(self, index, site):

        new_index = self.p(index, (site - 1) % self.L)

        if new_index is None:
            return None

        new_index = self.p(new_index, (site + 1) % self.L)

        if new_index is None:
            return None

        new_index = self.x(new_index, site)

        return new_index

    def translate(self, index, shift = 1):
        if index is None:
            return None

        state = self.state(index)
        translated_state = state[-shift:] + state[:-shift]
        return self.getIndex(translated_state)


def build_pxp_hamiltonian(state):
    """Construct the PXP Hamiltonian in the original 2**L basis.

    Each allowed spin flip contributes a unit matrix element. Periodic
    neighbors and the bit convention are defined by ``state.pxp``.
    The implementation intentionally matches the notebook's sparse assembly.
    """
    rows = []
    cols = []
    data = []

    for i in range(state.dim):
        for site in range(state.L):
            j = state.pxp(i, site)

            if j is not None:
                rows.append(j)
                cols.append(i)
                data.append(1.0)

    H = csr_matrix((data, (rows, cols)), shape=(state.dim, state.dim))
    return H
