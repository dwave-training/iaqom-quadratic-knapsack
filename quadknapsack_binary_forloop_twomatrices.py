"""
Requirements:
    Objective: Maximize the total value of products in the container.
    Constraint: The total weight of the selected products cannot exceed the container's weight limit.
Given constants:
    individual_values_matrix (array): The individual value of each product.
    pairwise_interaction (array): The interaction value associated with selecting pairs of products together.
    weights (array): The weight of each product.
    weight_limit (int): The weight capacity of the shipping container.
"""

# TODO: Import any required packages.
import numpy as np
from dwave.optimization import Model

# Initialize the nonlinear model object called `model_two_for`.
model_two_for = Model()

# Constants:
# The individual value of each product.
individual_values_matrix = np.array([6, 5, 8])

# The interaction value associated with selecting pairs of products together.
pairwise_interaction = np.array([[0, 4, 3], [4, 0, 2], [3, 2, 0]])

# The weight of each product.
weights = np.array([2, 3, 4])

# The weight limit of the shipping container.
weight_limit = 8

# Number of available products to pick from.
n = len(weights)

# Add the constants to the model object.
individual_values = model_two_for.constant(individual_values_matrix)
product_weights = model_two_for.constant(weights)
container_weight_limit = model_two_for.constant(weight_limit)

# TODO: Add the constant `pairwise_interaction` to the model object and name it `interaction_values`.


# Define the binary variable and store it in `products`.
products = model_two_for.binary(n)

# Objective function: Maximize the total value of products in the container.
# Define the linear objective.
linear_obj = (individual_values * products).sum()

# TODO: Define the quadratic objective using a for loop, and store it in `quadratic_obj`.
# Hint: Use `sum()` with a generator expression containing nested `for` clauses over all unique pairs (i < j).


# TODO: Set the objective function.


# Add the constraint: The total weight of selected products cannot exceed the container's weight limit.
model_two_for.add_constraint((product_weights * products).sum() <= container_weight_limit)

# TODO: Lock the model explicitly to prevent changes.


# TODO: Instantiate the nonlinear sampler and name it `sampler`.


# TODO: Submit the nonlinear model to the Stride hybrid solver. Use the label "Quadknap_binary_forloop_twomatrices", which is case-sensitive and uses an underscore.


# Process and print solution
print(
    "\nSubmit the quadratic knapsack problem to the Stride hybrid solver using an objective function with a for loop and two separate matrices for individual and interaction values.\n"
)
"""Read in the solution returned using `state(0)` and print it to the console."""

# TODO: Return the best solution for the binary variable symbol and store it in `products_state`.


# TODO: Return the best solution's objective value and store it in `objective_value`.


print(f"Objective Value of the best solution: {objective_value}")
print(f"Products (at state 0): {products_state}")
