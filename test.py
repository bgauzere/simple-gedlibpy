from ged import GED, get_nb_edit_operations
from gklearn.utils import load_dataset
#from gklearn.ged.util import compute_ged


def compute_ged(Gi, Gj, edit_cost, method='BIPARTITE'):
    """
    Compute GED between two graph according to edit_cost
    """
    dis, pi_forward, pi_backward = GED(Gi, Gj, lib='gedlibpy',
                                       cost='CONSTANT', method=method,
                                       edit_cost_constant=edit_cost,
                                       stabilizer='min',
                                       repeat=20)
    n_eo_tmp = get_nb_edit_operations(Gi, Gj, pi_forward, pi_backward)
    return dis, n_eo_tmp


G, y, _ = load_dataset('./data/simple_test.ds')
dis, _ = compute_ged(G[0], G[1], edit_cost=[3, 1, 1, 3, 1, 1])
print(dis)
