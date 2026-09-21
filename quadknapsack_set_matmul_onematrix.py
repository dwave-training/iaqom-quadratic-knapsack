"""
Requirements:
    Objective: Maximize the total value of products in the container.
    Constraint: The total weight of the selected products cannot exceed the container's weight limit.
Given constants:
    values_matrix (array): The values of individual products and the interactions associated with selecting pairs of products together.
    weights (array): The weight of each product.
    weight_limit (int): The weight capacity of the shipping container.
"""

# The required packages
import numpy as np
from dwave.optimization import Model
from dwave.system import StrideHybridSolver

# Initialize the nonlinear model object.
model = Model()

# Constants
# The values of individual products and the interactions associated with selecting pairs of products together.
values_matrix = np.array([[6, 2, 1.5], [2, 5, 1], [1.5, 1, 8]])

# The weight of each product.
weights = np.array([2, 3, 4])

# The weight limit of the shipping container.
weight_limit = 8

# Number of available products to pick from.
n = len(weights)

# Add the constants to the model object.
values = model.constant(values_matrix)
product_weights = model.constant(weights)
container_weight_limit = model.constant(weight_limit)
eye = model.constant(np.eye(n))  # used to build the indicator vector

# Define the decision variable: set of packed product indices (dynamic size 0 to n)
products = model.set(n)

# Build a fixed-shape binary indicator from the set
x = eye[products].sum(axis=0)

# Set the objective function: Maximize the total value of products in the container.
model.minimize(-(x @ values @ x).sum())

# Add the constraint: The total weight of selected products cannot exceed the container's weight limit.
model.add_constraint(product_weights[products].sum() <= container_weight_limit)

# Lock the model explicitly to prevent changes.
model.lock()

# Instantiate the nonlinear sampler.
sampler = StrideHybridSolver()

# Submit the nonlinear model to the Stride hybrid solver.
sampler.sample(model, label="Quadknap_set_matmul_onematrix")

# Return the best solution for the set variable symbol and its objective value.
print(
    f"The best solution returned, products={products.state(0)} results in the objective value of {model.objective.state(0)}."
)
