"""
combined_solution_quality_time.py

Self-contained script that:
  1. Generates a shared random matrix in-memory.
  2. Builds and runs both the binary-variable formulation and the set-variable
     formulation of the same quadratic knapsack problem across a range of solver
     time limits.
  3. Plots both formulations' mean-objective-vs-time-limit curves on the same,
     color-coded figure for direct comparison.

Matrix generation notes:
  - Off-diagonal (pairwise interaction) entries are drawn from [LOW, HIGH),
    symmetrized, and then ~ZERO_FRACTION of them are randomly zeroed out
    (default 50%), while keeping the matrix symmetric.
  - The diagonal is filled with random nonzero integers.
  - Matrix size N is a hyperparameter.

Weight/capacity notes:
  - Item weights are random integers in [WEIGHT_LOW, WEIGHT_HIGH).
  - The knapsack weight_limit ("capacity") is set to CAPACITY_FRACTION of the
    total weight of all items. CAPACITY_FRACTION should be chosen in the
    range 0.2-0.5 (20%-50% of total weight).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dwave.optimization import Model
from dwave.system import StrideHybridSolver

# Hyperparameters
N = 300  # matrix / problem size (n x n). Default 10x10.
SEED = 42  # RNG seed, fixed for reproducibility

# Matrix (pairwise interaction) generation
VALUE_LOW, VALUE_HIGH = 1, 25  # off-diagonal value range before zeroing
DIAG_LOW, DIAG_HIGH = 1, 100  # diagonal value range
ZERO_FRACTION = 0.5  # fraction of off-diagonal entries set to 0

# Weights / capacity
WEIGHT_LOW, WEIGHT_HIGH = 1, 30  # per-item weight range
CAPACITY_FRACTION = 0.5  # weight_limit = CAPACITY_FRACTION * sum(weights)
# choose within [0.2, 0.5]

# Solver run configuration
TIME_LIMITS = [5, 10, 20, 60, 90]  # seconds
SAMPLES_PER_TIME = 3

# Additonal constraints to add complexity to the problem (optional)
ADDITIONAL_CONSTRAINTS = False  # Set to True to add additional constraints
k = 5  # Number of items in the random subset S for the additional constraint

if ADDITIONAL_CONSTRAINTS:
    rng_constraints = np.random.default_rng(SEED)
    S_1 = rng_constraints.choice(N, size=k, replace=False)
    S_2 = rng_constraints.choice(N, size=k + 1, replace=False)
    S_3 = rng_constraints.choice(N, size=k + 2, replace=False)


def generate_matrix(n, seed, low=1, high=25, diag_low=1, diag_high=100, zero_fraction=0.5):
    """Generate a random, symmetric, nonzero-diagonal integer matrix where
    ~zero_fraction of the off-diagonal (pairwise interaction) entries are 0.
    - Off-diagonal entries are random integers in [low, high), symmetrized.
    - A random symmetric mask zeroes out `zero_fraction` of the off-diagonal
      entries (applied to the upper triangle, then mirrored).
    - The diagonal is overwritten with random nonzero integers in
      [diag_low, diag_high].
    """
    rng = np.random.default_rng(seed)

    A = rng.integers(low=low, high=high, size=(n, n))
    matrix = (A + A.T) // 2

    # Build a symmetric zero-mask covering the requested fraction of the
    # off-diagonal entries.
    zero_mask_upper = rng.random((n, n)) < zero_fraction
    zero_mask_upper = np.triu(zero_mask_upper, k=1)
    zero_mask = zero_mask_upper | zero_mask_upper.T
    matrix[zero_mask] = 0

    diag_values = rng.integers(low=diag_low, high=diag_high, size=n)
    np.fill_diagonal(matrix, diag_values)

    return matrix.astype(int)


def generate_weights(n, seed, low=1, high=30):
    rng = np.random.default_rng(seed)
    return rng.integers(low, high, size=n)


# Generate the shared matrix and weights.
values_matrix = generate_matrix(N, SEED, VALUE_LOW, VALUE_HIGH, DIAG_LOW, DIAG_HIGH, ZERO_FRACTION)
weights = generate_weights(N, SEED, WEIGHT_LOW, WEIGHT_HIGH)
weight_limit = CAPACITY_FRACTION * weights.sum()

if weight_limit < weights.min():
    raise ValueError(
        f"weight_limit ({weight_limit:.2f}) is smaller than the lightest item "
        f"({weights.min()}) - no item could ever be selected. Increase "
        f"CAPACITY_FRACTION or check WEIGHT_LOW/WEIGHT_HIGH."
    )


# Precompute the half pairwise interaction matrix used by both formulations.
half_values_interaction_matrix = 1 / 2 * values_matrix
half_values_interaction_matrix[np.diag_indices_from(half_values_interaction_matrix)] = np.diag(
    values_matrix
)


# Formulation 1: binary
def build_binary_model():
    model_binary = Model()

    # Add the constants to the model object
    values = model_binary.constant(half_values_interaction_matrix)
    product_weights = model_binary.constant(weights)
    container_weight_limit = model_binary.constant(weight_limit)

    # Define the binary variable
    products = model_binary.binary(N)

    # Objective function and constraint
    model_binary.minimize(-(products @ values @ products))
    model_binary.add_constraint((product_weights * products).sum() <= container_weight_limit)

    if ADDITIONAL_CONSTRAINTS:
        model_binary.add_constraint(
            products.sum() <= N // 2
        )  # At most half the total number of items can be selected
        # add a constraint that at least one item from the subset S must be selected
        model_binary.add_constraint(products[S_1].sum() >= 1)
        model_binary.add_constraint(products[S_2].sum() >= 1)
        model_binary.add_constraint(products[S_3].sum() >= 1)

    model_binary.lock()

    return model_binary, products


# Formulation 2: set variable
def build_set_model():
    model_set = Model()

    identity_matrix = np.eye(N)

    # Add the constants to the model object
    values = model_set.constant(half_values_interaction_matrix)
    product_weights = model_set.constant(weights)
    container_weight_limit = model_set.constant(weight_limit)

    # Define the eye matrix for building the indicator vector
    eye = model_set.constant(identity_matrix)

    # Define the set variable
    products = model_set.set(N)

    # Linear term: total weight (advanced indexing works with a set)
    total_weight = product_weights[products].sum()
    products_selected = eye[products].sum(axis=0)
    # products_selected = identity_matrix[products].sum(axis=0)
    # -> model_set.minimize(-(products_selected @ values @ products_selected))
    # Objective function and constraint
    model_set.minimize(-(products_selected @ values @ products_selected))
    model_set.add_constraint(total_weight <= container_weight_limit)

    if ADDITIONAL_CONSTRAINTS:
        model_set.add_constraint(
            products.size() <= N // 2
        )  # At most half the total number of items can be selected
        # add a constraint that at least one item from the subset S must be selected
        model_set.add_constraint(products_selected[S_1].sum() >= 1)
        model_set.add_constraint(products_selected[S_2].sum() >= 1)
        model_set.add_constraint(products_selected[S_3].sum() >= 1)

    model_set.lock()

    return model_set, products


# Run both formulations across the same time limits / samples.
FORMULATIONS = [
    ("binary", build_binary_model),
    ("set", build_set_model),
]
rows_by_formulation = {label: [] for label, _ in FORMULATIONS}

# print state size and node size for each formulation
for label, build_fn in FORMULATIONS:
    model, products = build_fn()
    print(
        f"{label} formulation: state size = {model.state_size()}, node size = {model.num_nodes()}, decision state size ={model.decision_state_size()}"
    )

# Loop over time limits and samples, running both formulations for each combination.
with StrideHybridSolver() as sampler:
    for requested_time_limit in TIME_LIMITS:
        for sample_id in range(SAMPLES_PER_TIME):
            for label, build_fn in FORMULATIONS:
                model, products = build_fn()
                sampler.sample(model, time_limit=requested_time_limit).result()

                rows_by_formulation[label].append(
                    {
                        "formulation": label,
                        "requested_time_limit": requested_time_limit,
                        "sample_id": sample_id,
                        "selected_products": [int(i) for i in products.state(0)],
                        "minimized_objective": model.objective.state(0).item(),
                    }
                )


# Summarize + combined, color-coded plot
def summarize(rows):
    df = pd.DataFrame(rows)
    summary = (
        df.groupby("requested_time_limit")["minimized_objective"].agg(["min", "mean"]).reset_index()
    )
    return df, summary


binary_df, binary_summary = summarize(rows_by_formulation["binary"])
set_df, set_summary = summarize(rows_by_formulation["set"])

total_runs = SAMPLES_PER_TIME
suffix = f"n{N}_runs{total_runs}_additional_constraints{ADDITIONAL_CONSTRAINTS}_k{k}"

print("\nBinary formulation - solution quality summary:")
print(binary_summary.to_string(index=False))

print("\nSet formulation - solution quality summary:")
print(set_summary.to_string(index=False))

# Combine raw data from both formulations
combined_df = pd.concat([binary_df, set_df], ignore_index=True)

# Comparison plot
plt.figure(figsize=(8, 6))
plt.plot(
    binary_summary["requested_time_limit"],
    binary_summary["mean"],
    marker="o",
    color="tab:blue",
    label="Binary formulation",
)
plt.plot(
    set_summary["requested_time_limit"],
    set_summary["mean"],
    marker="s",
    color="tab:red",
    label="Set formulation",
)
plt.xlabel("Time limit", fontsize=16)
plt.ylabel("Objective value", fontsize=16)
plt.title(
    f"Solution quality over time: binary vs. set formulation (N={N}, runs={total_runs}, additional_constraints={ADDITIONAL_CONSTRAINTS}, k={k})",
    fontsize=16,
)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(f"combined_solution_quality_time_{suffix}.png")
plt.show()
