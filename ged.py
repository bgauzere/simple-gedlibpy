#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 18:44:59 2019

@author: ljia
"""
import numpy as np
import networkx as nx
from tqdm import tqdm
import sys
import multiprocessing
from multiprocessing import Pool
from functools import partial

# Requirers a good PYTHONPATH
import librariesImport
import gedlibpy


def GED(g1, g2, lib='gedlibpy', cost='CHEM_1', method='IPFP',
        edit_cost_constant=[], stabilizer='min', repeat=50):
    """
    Compute GED for 2 graphs.
    """
    if lib == 'gedlibpy':
        def convertGraph(G):
            """Convert a graph to the proper NetworkX format that can be
            recognized by library gedlibpy.
            """
            G_new = nx.Graph()
            for nd, attrs in G.nodes(data=True):
                G_new.add_node(str(nd), chem=attrs['atom_symbol'])
#                G_new.add_node(str(nd), x=str(attrs['attributes'][0]),
#                               y=str(attrs['attributes'][1]))
            for nd1, nd2, attrs in G.edges(data=True):
                G_new.add_edge(str(nd1), str(nd2), valence=attrs['bond_type'])
#                G_new.add_edge(str(nd1), str(nd2))

            return G_new

        gedlibpy.restart_env()
        gedlibpy.add_nx_graph(convertGraph(g1), "")
        gedlibpy.add_nx_graph(convertGraph(g2), "")

        listID = gedlibpy.get_all_graph_ids()
        gedlibpy.set_edit_cost(cost, edit_cost_constant=edit_cost_constant)
        gedlibpy.init()
        gedlibpy.set_method(method, "")
        gedlibpy.init_method()

        g = listID[0]
        h = listID[1]
        if stabilizer == None:
            gedlibpy.run_method(g, h)
            pi_forward = gedlibpy.get_forward_map(g, h)
            pi_backward = gedlibpy.get_backward_map(g, h)
            upper = gedlibpy.get_upper_bound(g, h)
            lower = gedlibpy.get_lower_bound(g, h)
        elif stabilizer == 'mean':
            # @todo: to be finished...
            upper_list = [np.inf] * repeat
            for itr in range(repeat):
                gedlibpy.run_method(g, h)
                upper_list[itr] = gedlibpy.get_upper_bound(g, h)
                pi_forward = gedlibpy.get_forward_map(g, h)
                pi_backward = gedlibpy.get_backward_map(g, h)
                lower = gedlibpy.get_lower_bound(g, h)
            upper = np.mean(upper_list)
        elif stabilizer == 'median':
            if repeat % 2 == 0:
                repeat += 1
            upper_list = [np.inf] * repeat
            pi_forward_list = [0] * repeat
            pi_backward_list = [0] * repeat
            for itr in range(repeat):
                gedlibpy.run_method(g, h)
                upper_list[itr] = gedlibpy.get_upper_bound(g, h)
                pi_forward_list[itr] = gedlibpy.get_forward_map(g, h)
                pi_backward_list[itr] = gedlibpy.get_backward_map(g, h)
                lower = gedlibpy.get_lower_bound(g, h)
            upper = np.median(upper_list)
            idx_median = upper_list.index(upper)
            pi_forward = pi_forward_list[idx_median]
            pi_backward = pi_backward_list[idx_median]
        elif stabilizer == 'min':
            upper = np.inf
            for itr in range(repeat):
                gedlibpy.run_method(g, h)
                upper_tmp = gedlibpy.get_upper_bound(g, h)
                if upper_tmp < upper:
                    upper = upper_tmp
                    pi_forward = gedlibpy.get_forward_map(g, h)
                    pi_backward = gedlibpy.get_backward_map(g, h)
                    lower = gedlibpy.get_lower_bound(g, h)
                if upper == 0:
                    break
        elif stabilizer == 'max':
            upper = 0
            for itr in range(repeat):
                gedlibpy.run_method(g, h)
                upper_tmp = gedlibpy.get_upper_bound(g, h)
                if upper_tmp > upper:
                    upper = upper_tmp
                    pi_forward = gedlibpy.get_forward_map(g, h)
                    pi_backward = gedlibpy.get_backward_map(g, h)
                    lower = gedlibpy.get_lower_bound(g, h)
        elif stabilizer == 'gaussian':
            pass

        dis = upper

        # make the map label correct (label remove map as np.inf)
        nodes1 = [n for n in g1.nodes()]
        nodes2 = [n for n in g2.nodes()]
        nb1 = nx.number_of_nodes(g1)
        nb2 = nx.number_of_nodes(g2)
        pi_forward = [nodes2[pi] if pi < nb2 else np.inf for pi in pi_forward]
        pi_backward = [nodes1[pi] if pi <
                       nb1 else np.inf for pi in pi_backward]

    return dis, pi_forward, pi_backward


def GED_n(Gn, lib='gedlibpy', cost='CHEM_1', method='IPFP',
          edit_cost_constant=[], stabilizer='min', repeat=50):
    """
    Compute GEDs for a group of graphs.
    """
    if lib == 'gedlibpy':
        def convertGraph(G):
            """Convert a graph to the proper NetworkX format that can be
            recognized by library gedlibpy.
            """
            G_new = nx.Graph()
            for nd, attrs in G.nodes(data=True):
                G_new.add_node(str(nd), chem=attrs['atom_symbol'])
            for nd1, nd2, attrs in G.edges(data=True):
                #                G_new.add_edge(str(nd1), str(nd2), valence=attrs['bond_type'])
                G_new.add_edge(str(nd1), str(nd2))

            return G_new

        # gedlibpy.restart_env()
        gedlibpy.add_nx_graph(convertGraph(g1), "")
        gedlibpy.add_nx_graph(convertGraph(g2), "")

        listID = gedlibpy.get_all_graph_ids()
        gedlibpy.set_edit_cost(cost, edit_cost_constant=edit_cost_constant)
        gedlibpy.init()
        gedlibpy.set_method(method, "")
        gedlibpy.init_method()

        g = listID[0]
        h = listID[1]
        if stabilizer == None:
            gedlibpy.run_method(g, h)
            pi_forward = gedlibpy.get_forward_map(g, h)
            pi_backward = gedlibpy.get_backward_map(g, h)
            upper = gedlibpy.get_upper_bound(g, h)
            lower = gedlibpy.get_lower_bound(g, h)
        elif stabilizer == 'min':
            upper = np.inf
            for itr in range(repeat):
                gedlibpy.run_method(g, h)
                upper_tmp = gedlibpy.get_upper_bound(g, h)
                if upper_tmp < upper:
                    upper = upper_tmp
                    pi_forward = gedlibpy.get_forward_map(g, h)
                    pi_backward = gedlibpy.get_backward_map(g, h)
                    lower = gedlibpy.get_lower_bound(g, h)
                if upper == 0:
                    break

        dis = upper

        # make the map label correct (label remove map as np.inf)
        nodes1 = [n for n in g1.nodes()]
        nodes2 = [n for n in g2.nodes()]
        nb1 = nx.number_of_nodes(g1)
        nb2 = nx.number_of_nodes(g2)
        pi_forward = [nodes2[pi] if pi < nb2 else np.inf for pi in pi_forward]
        pi_backward = [nodes1[pi] if pi <
                       nb1 else np.inf for pi in pi_backward]

    return dis, pi_forward, pi_backward


def ged_median(Gn, Gn_median, verbose=False, params_ged={'lib': 'gedlibpy',
                                                         'cost': 'CHEM_1', 'method': 'IPFP', 'edit_cost_constant': [],
                                                         'stabilizer': 'min', 'repeat': 50}, parallel=False):
    if parallel:
        len_itr = int(len(Gn))
        pi_forward_list = [[] for i in range(len_itr)]
        dis_list = [0 for i in range(len_itr)]

        itr = range(0, len_itr)
        n_jobs = multiprocessing.cpu_count()
        if len_itr < 100 * n_jobs:
            chunksize = int(len_itr / n_jobs) + 1
        else:
            chunksize = 100

        def init_worker(gn_toshare, gn_median_toshare):
            global G_gn, G_gn_median
            G_gn = gn_toshare
            G_gn_median = gn_median_toshare
        do_partial = partial(_compute_ged_median, params_ged)
        pool = Pool(processes=n_jobs, initializer=init_worker,
                    initargs=(Gn, Gn_median))
        if verbose:
            iterator = tqdm(pool.imap_unordered(do_partial, itr, chunksize),
                            desc='computing GEDs', file=sys.stdout)
        else:
            iterator = pool.imap_unordered(do_partial, itr, chunksize)
        for i, dis_sum, pi_forward in iterator:
            pi_forward_list[i] = pi_forward
            dis_list[i] = dis_sum
#            print('\n-------------------------------------------')
#            print(i, j, idx_itr, dis)
        pool.close()
        pool.join()

    else:
        dis_list = []
        pi_forward_list = []
        for idx, G in tqdm(enumerate(Gn), desc='computing median distances',
                           file=sys.stdout) if verbose else enumerate(Gn):
            dis_sum = 0
            pi_forward_list.append([])
            for G_p in Gn_median:
                dis_tmp, pi_tmp_forward, pi_tmp_backward = GED(G, G_p,
                                                               **params_ged)
                pi_forward_list[idx].append(pi_tmp_forward)
                dis_sum += dis_tmp
            dis_list.append(dis_sum)

    return dis_list, pi_forward_list


def _compute_ged_median(params_ged, itr):
    #    print(itr)
    dis_sum = 0
    pi_forward = []
    for G_p in G_gn_median:
        dis_tmp, pi_tmp_forward, pi_tmp_backward = GED(G_gn[itr], G_p,
                                                       **params_ged)
        pi_forward.append(pi_tmp_forward)
        dis_sum += dis_tmp

    return itr, dis_sum, pi_forward


def get_nb_edit_operations(g1, g2, forward_map, backward_map):
    """Compute the number of each edit operations.
    """
    n_vi = 0
    n_vr = 0
    n_vs = 0
    n_ei = 0
    n_er = 0
    n_es = 0

    nodes1 = [n for n in g1.nodes()]
    for i, map_i in enumerate(forward_map):
        if map_i == np.inf:
            n_vr += 1
        elif g1.nodes[nodes1[i]]['atom_symbol'] != g2.nodes[map_i]['atom_symbol']:
            n_vs += 1
    for map_i in backward_map:
        if map_i == np.inf:
            n_vi += 1

#    idx_nodes1 = range(0, len(node1))

    edges1 = [e for e in g1.edges()]
    nb_edges2_cnted = 0
    for n1, n2 in edges1:
        idx1 = nodes1.index(n1)
        idx2 = nodes1.index(n2)
        # one of the nodes is removed, thus the edge is removed.
        if forward_map[idx1] == np.inf or forward_map[idx2] == np.inf:
            n_er += 1
        # corresponding edge is in g2. Edge label is not considered.
        elif (forward_map[idx1], forward_map[idx2]) in g2.edges() or \
                (forward_map[idx2], forward_map[idx1]) in g2.edges():
            nb_edges2_cnted += 1
        # corresponding nodes are in g2, however the edge is removed.
        else:
            n_er += 1
    n_ei = nx.number_of_edges(g2) - nb_edges2_cnted

    return n_vi, n_vr, n_vs, n_ei, n_er, n_es
