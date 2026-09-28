"""
Requirements:
    Objective: Maximize the total value of products in the container.
    Constraint: The total weight of the selected products cannot exceed the container's weight limit.
Given constants:
    values_matrix (array): The values of individual products and the interactions associated with selecting pairs of products together.
    weights (array): The weight of each product.
    weight_limit (int): The weight capacity of the shipping container.
"""

# The required packages.
import numpy as np
from dwave.optimization import Model
from dwave.system import StrideHybridSolver

# Initialize the nonlinear model object.
model_set = Model()

# Constants
# The values of individual products and the interactions associated with selecting pairs of products together.
values_matrix = np.array([[6, 2, 1.5], [2, 5, 1], [1.5, 1, 8]])

# The weight of each product.
weights = np.array([2, 3, 4])

# The weight limit of the shipping container.
weight_limit = 8

# Number of available products to pick from.
n = len(weights)

# Identity matrix of dimensions nxn
identity_matrix = np.eye(n)

# Add the constants to the model object.
values = model_set.constant(values_matrix)
product_weights = model_set.constant(weights)
container_weight_limit = model_set.constant(weight_limit)

# Add the constant `identity_matrix` to the model object. It is used to build the indicator vector.
eye = model_set.constant(identity_matrix)  

#TODO: Define the set variable and store it in `products`. Use `n` to determine the total number of elements in the set. 
products = model_set.set(n)

#TODO: Build a fixed-shape binary indicator vector of length-n from the set and store it in `products_selected`. 
# Hint: Use the selected `products` indices to select the corresponding rows of the identity matrix created.
# Use `.sum(axis=0)` to add the selected rows column by column.
products_selected = eye[products].sum(axis=0)

#TODO: Set the objective function: Maximize the total value of products in the container.
model_set.minimize(- (products_selected @ values @ products_selected) )

# Add the constraint: The total weight of selected products cannot exceed the container's weight limit.
model_set.add_constraint(product_weights[products].sum() <= container_weight_limit)

# Lock the model explicitly to prevent changes.
model_set.lock()

# Instantiate the nonlinear sampler.
sampler = StrideHybridSolver()

# Submit the nonlinear model to the Stride hybrid solver.
sampler.sample(model_set, label="Quadknap_set_matmul_onematrix")

# Return the best solution for the set variable symbol and its objective value.
print(
    f"The best solution returned using a set as the decision variable, products={products.state(0)} results in the objective value of {model_set.objective.state(0)}."
)
