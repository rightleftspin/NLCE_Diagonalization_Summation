#!/usr/bin/env python3
import numpy as np
import json
import matplotlib.pyplot as plt
import copy
import time
import sys
import os

import exact_diagonalization as ed
import property_solvers as ps
from model_specific_functions import model_info

def nlce_summation_main(temp_range, granularity, final_order, property_type, model, nlce_type, nlce_data_dir, proper_property_data_dir):
    temp_grid = np.linspace(temp_range[0], temp_range[1], num=granularity)
    weight_dict_ordered = {}
    weight_dict = {}
    
    for order in range(1, final_order + 1):
        start = time.time()
        graph_property_info = ps.solve_property_for_order(property_type, model, nlce_data_dir, proper_property_data_dir, order, nlce_type, temp_grid)
    
        subgraph_mult = open(f'{nlce_data_dir}/{nlce_type}/subgraph_mult_{nlce_type}_{order}.json')
        graph_mult = open(f'{nlce_data_dir}/{nlce_type}/graph_mult_{nlce_type}_{order}.json')
    
        subgraph_mult_dict = json.load(subgraph_mult)
        graph_mult_dict = json.load(graph_mult)
    
        weight_dict_ordered[order] = {}
    
        for graph_id in subgraph_mult_dict:
            property_unweighted = np.array(graph_property_info[graph_id])
            if order > 1:
                for subgraph_id in subgraph_mult_dict[graph_id]:
    
                    property_unweighted -= subgraph_mult_dict[graph_id][subgraph_id] * weight_dict[subgraph_id]
    
            weight_dict_ordered[order][graph_id] = graph_mult_dict[graph_id] * property_unweighted
            weight_dict[graph_id] = property_unweighted
        print(f"Finishing order {order} in {time.time() - start:5f} sec")
    
    return(weight_dict_ordered, temp_grid)

def sum_by_order_ascending(ordered_property_dict, temp_grid):
    final_property_grid_by_order = []
    cumulative_order = np.zeros_like(temp_grid)
    
    for order in ordered_property_dict:
        property_dict = ordered_property_dict[order]
        for graph_id in property_dict:
            cumulative_order += property_dict[graph_id]
    
        final_property_grid_by_order.append(copy.deepcopy(cumulative_order))

    return(final_property_grid_by_order)

def generate_plot_by_order(property_type, model, output_dir, property_data_by_order, temp_data, starting_order):
    final_order = len(property_data_by_order)
    for order in range(starting_order, final_order):
        plt.plot(temp_data, property_data_by_order[order], label = f"{order + 1}")
    
    plt.xlabel("log(Temperature)")
    plt.ylabel(f"{property_type.capitalize()}")
    plt.title(f"{model.capitalize()} {property_type.capitalize()} vs log(Temperature) NLCE Order {final_order}")
    plt.legend()
    plt.xscale("log")
    
    plt.savefig(f"{output_dir}/{property_type}_{final_order}.pdf")
    plt.close()
    return()

def plot_for_property(input_array, temp_range):
    nlce_type, final_order, model, property_type = input_array
    final_order = int(final_order)
    if (model not in model_info) or (property_type not in ps.property_information):
        raise ValueError("Not a valid Model or Property Type")

    granularity = 500
    starting_order_plot = 6
    nlce_data_dir = "./Data/NLCE_Data"
    property_data_dir = "./Data/Property_Data"
    proper_property_data_dir = f"{property_data_dir}/{nlce_type}/{model}/{property_type}/{int(temp_range[0]*10)}_{int(temp_range[1]*10)}/"
    os.makedirs(proper_property_data_dir, exist_ok=True)

    prop_by_order_dict, temp_grid = nlce_summation_main(temp_range, granularity, final_order, property_type, model, nlce_type, nlce_data_dir, proper_property_data_dir)

    prop_by_order_list = sum_by_order_ascending(prop_by_order_dict, temp_grid)

    generate_plot_by_order(property_type, model, proper_property_data_dir, prop_by_order_list, temp_grid, starting_order_plot)

    return()


plot_for_property(sys.argv[1:5], (.5, 20))