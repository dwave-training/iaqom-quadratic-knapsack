"""
quadknapsack_set_binary_comparison.py

Self-contained script that:
    1. Generates a shared random matrix.
    2. Builds and runs both the binary-variable formulation and the set-variable
        formulation of the same quadratic knapsack problem across a range of solver
        time limits.
    3. Plots both formulations' mean-objective-vs-time-limit curves on the same,
        color-coded figure for direct comparison.

Matrix generation notes:
    - Off-diagonal (pairwise interaction) entries are drawn from
        [VALUE_LOW, VALUE_HIGH), symmetrized, and then approximately ZERO_FRACTION
        of them are randomly zeroed out (default 50%), while keeping the matrix
        symmetric.
    - The diagonal is filled with random nonzero integers.
    - Matrix size N is a hyperparameter.

Weight/capacity notes:
    - Item weights are random integers in [WEIGHT_LOW, WEIGHT_HIGH).
    - The knapsack `weight_limit` ("capacity") is set to CAPACITY_FRACTION of the
        total weight of all items. CAPACITY_FRACTION should be chosen in the
        range 0.2-0.5 (20%-50% of total weight).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dwave.optimization import Model
from dwave.system import StrideHybridSolver

# Hyperparameters
N = 300  # The number of items, which is also the dimension of the n x n values matrix.
SEED = 42  # The random number generator seed is fixed for reproducibility.

# Parameters for generating the pairwise interaction matrix.
VALUE_LOW, VALUE_HIGH = 1, 25  # The range of off-diagonal values before some are zeroed out.
DIAG_LOW, DIAG_HIGH = 1, 100  # The range of diagonal values.
ZERO_FRACTION = 0.5  # The fraction of off-diagonal entries that are set to 0.

# Weights / capacity
WEIGHT_LOW, WEIGHT_HIGH = 1, 30  # The range of weights for each item.
CAPACITY_FRACTION = (
    0.5  # Choose a value within [0.2, 0.5], weight_limit = CAPACITY_FRACTION * sum(weights)
)

# Solver run configuration
TIME_LIMITS = [5, 10, 20, 60, 90, 120]  # The requested time limits in seconds.
SAMPLES_PER_TIME = 1  # The number of samples taken at each time limit.


def generate_matrix(n, seed, low=1, high=25, diag_low=1, diag_high=100, zero_fraction=0.5):
    """Generate a random, symmetric, nonzero-diagonal integer matrix where
    approximately `zero_fraction` of the off-diagonal (pairwise interaction)
    entries are 0.
    - Off-diagonal entries are random integers in [low, high), symmetrized.
    - A random symmetric mask zeroes out `zero_fraction` of the off-diagonal
      entries (applied to the upper triangle, then mirrored).
    - The diagonal is overwritten with random nonzero integers in
      [diag_low, diag_high).

    Args:
        n: The dimension of the square matrix.
        seed: The random number generator seed.
        low: The lower bound for off-diagonal values (inclusive).
        high: The upper bound for off-diagonal values (exclusive).
        diag_low: The lower bound for diagonal values (inclusive).
        diag_high: The upper bound for diagonal values (exclusive).
        zero_fraction: The fraction of off-diagonal entries to set to 0.

    Returns:
        A symmetric n x n integer matrix with the specified properties.
    """
    rng = np.random.default_rng(seed)

    A = rng.integers(low=low, high=high, size=(n, n))
    matrix = (A + A.T) // 2

    # Build a symmetric zero-mask covering the requested fraction of the off-diagonal entries.
    zero_mask_upper = rng.random((n, n)) < zero_fraction
    zero_mask_upper = np.triu(zero_mask_upper, k=1)
    zero_mask = zero_mask_upper | zero_mask_upper.T
    matrix[zero_mask] = 0

    diag_values = rng.integers(low=diag_low, high=diag_high, size=n)
    np.fill_diagonal(matrix, diag_values)

    return matrix.astype(int)


def generate_weights(n, seed, low=1, high=30):
    """Generate a random weight vector for the knapsack problem.

    Args:
        n: The number of items.
        seed: The random number generator seed.
        low: The lower bound for weights (inclusive).
        high: The upper bound for weights (exclusive).

    Returns:
        A length-n integer array of weights.
    """
    rng = np.random.default_rng(seed)
    return rng.integers(low, high, size=n)


# Formulation 1: Using a binary variable
def build_binary_model(half_values_interaction_matrix, weights, weight_limit):
    """Build the binary variable formulation of the quadratic knapsack problem.

    Returns:
        A tuple containing the model and the binary variable representing the selected products.
    """
    # Initialize the nonlinear model object.
    model_binary = Model()

    # Add the constants to the model object.
    values = model_binary.constant(half_values_interaction_matrix)
    product_weights = model_binary.constant(weights)
    container_weight_limit = model_binary.constant(weight_limit)

    # Define the binary variable.
    products = model_binary.binary(N)

    # Set the objective function: Maximize the total value of products in the container.
    model_binary.minimize(-(products @ values @ products))
    # Add the constraint: The total weight of selected products cannot exceed the container's weight limit.
    model_binary.add_constraint((product_weights * products).sum() <= container_weight_limit)

    model_binary.lock()

    return model_binary, products


# Formulation 2: Using a set variable
def build_set_model(half_values_interaction_matrix, weights, weight_limit):
    """Build the set variable formulation of the quadratic knapsack problem.

    Returns:
        A tuple containing the model and the set variable representing the selected products.
    """
    # Initialize the nonlinear model object.
    model_set = Model()

    # Identity matrix of dimensions n x n.
    identity_matrix = np.eye(N)

    # Add the constants to the model object.
    values = model_set.constant(half_values_interaction_matrix)
    product_weights = model_set.constant(weights)
    container_weight_limit = model_set.constant(weight_limit)

    # Add the identity matrix as a constant. It is used to build the indicator vector.
    eye = model_set.constant(identity_matrix)

    # Define the set variable.
    products = model_set.set(N)

    # Build a fixed-shape binary indicator vector of length n from the set.
    products_selected = eye[products].sum(axis=0)

    # Set the objective function and add the weight constraint.
    model_set.minimize(-(products_selected @ values @ products_selected))

    # Linear term: total weight (advanced indexing works with a set)
    total_weight = product_weights[products].sum()

    # Add the constraint: The total weight of selected products cannot exceed the container's weight limit.
    model_set.add_constraint(total_weight <= container_weight_limit)

    model_set.lock()

    return model_set, products


# Summarize the results and create a combined, color-coded plot.
def summarize(rows):
    """Summarize the results of the experiments.

    Args:
        rows: A list of dictionaries containing the raw results for each run.

    Returns:
        A tuple containing the raw DataFrame and a summary DataFrame with the minimum and mean
        minimized objective for each requested time limit.
    """
    df = pd.DataFrame(rows)
    summary = (
        df.groupby("requested_time_limit")["minimized_objective"].agg(["min", "mean"]).reset_index()
    )
    return df, summary


# Generate the shared matrix and weights.
values_matrix = generate_matrix(N, SEED, VALUE_LOW, VALUE_HIGH, DIAG_LOW, DIAG_HIGH, ZERO_FRACTION)
weights = generate_weights(N, SEED, WEIGHT_LOW, WEIGHT_HIGH)
weight_limit = CAPACITY_FRACTION * weights.sum()

if weight_limit < weights.min():
    raise ValueError(
        f"The weight limit ({weight_limit:.2f}) is smaller than the lightest item "
        f"({weights.min()}), so no item can be selected. Increase CAPACITY_FRACTION "
        "or lower WEIGHT_LOW and WEIGHT_HIGH."
    )

# Precompute the half pairwise interaction matrix used by both formulations.
half_values_interaction_matrix = 1 / 2 * values_matrix
half_values_interaction_matrix[np.diag_indices_from(half_values_interaction_matrix)] = np.diag(
    values_matrix
)

# Run both formulations across the same time limits / samples.
FORMULATIONS = [
    ("binary", lambda: build_binary_model(half_values_interaction_matrix, weights, weight_limit)),
    ("set", lambda: build_set_model(half_values_interaction_matrix, weights, weight_limit)),
]
rows_by_formulation = {label: [] for label, _ in FORMULATIONS}

# Print state size and node size for each formulation.
for label, build_fn in FORMULATIONS:
    model, products = build_fn()
    print(
        f"{label} formulation: state size = {model.state_size()}, node size = {model.num_nodes()}, decision state size = {model.decision_state_size()}"
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


# Retrieve the summarized results for both formulations.
binary_df, binary_summary = summarize(rows_by_formulation["binary"])
set_df, set_summary = summarize(rows_by_formulation["set"])

suffix = f"n{N}_runs{SAMPLES_PER_TIME}"

print("\nBinary formulation - solution quality summary:")
print(binary_summary.to_string(index=False))

print("\nSet formulation - solution quality summary:")
print(set_summary.to_string(index=False))

# Combine raw data from both formulations.
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
plt.xlabel("Time limit", fontsize=14)
plt.ylabel("Objective value", fontsize=14)
plt.title(
    "Binary vs. set formulation\n" f"Objective over time (N={N}, runs={SAMPLES_PER_TIME})",
    fontsize=12,
)
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(f"combined_solution_quality_time_{suffix}.png")
plt.show()
