"""
Requirements:
    Objective: Maximize the total value of products in the container.
    Constraint: The total weight of selected products cannot exceed the container's weight limit.
Given constants:
    individual_values_matrix (array): The individual value of each product.
    pairwise_interaction (array): The interaction value associated with selecting pairs of products together.
    weights (array): The weight of each product.
    weight_limit (int): The weight capacity of the shipping container.
"""

#TODO: Import any required packages.
import numpy as np
from dwave.optimization import Model


# Initialize the nonlinear model object called `model_two_matmul`.
model_two_matmul = Model()

# Constants:
# The individual value of each product.
individual_values_matrix = np.array([6, 5, 8])

# The interaction value associated with selecting pairs of products together.
pairwise_interaction = np.array([
						[0, 4, 3],
						[4, 0, 2],
						[3, 2, 0]
						])

# The weight of each product.
weights = np.array([2,3,4])

# The weight limit of the shipping container.
weight_limit = 8

# Number of avaiblable products to pick from.
n = len(weights)

#TODO: Define the half pairwise interaction matrix and name it `half_pairwise_interaction`.


# Add the constants to the model object.
individual_values = model_two_matmul.constant(individual_values_matrix)
product_weights = model_two_matmul.constant(weights)
container_weight_limit = model_two_matmul.constant(weight_limit)

#TODO: Add the constant `half_pairwise_interaction` to the model object and name it `interaction_values`.


# Define the binary variable and store it in `products`.
products = model_two_matmul.binary(n)

# Objective function: Maximize the total value of products in the container.
# Define the linear objective.
linear_obj = (individual_values * products).sum()

##TODO: Define the quadratic objective using the @ operator, and store it in `quadratic_obj`.


#TODO: Set the objective function.


# Add the constraint: The total weight of selected products cannot exceed the container's weight limit.
model_two_matmul.add_constraint((product_weights * products).sum() <= container_weight_limit)

#TODO: Lock the model explicitly to prevent changes.


#TODO: Instantiate the nonlinear sampler and name it `sampler`.


#TODO: Submit the nonlinear model to the Stride hybrid solver. Use the label "Quadknap_binary_matmul_twomatrices", which is case-sensitive and uses an underscore.


# Process and print solution
print("\nSubmit the quadratic knapsack problem to the Stride hybrid solver using the @ operator with two values matrices\n")
"""Read in the solution returned using `state(0)` and display solution."""

#TODO: Return the best solution for the binary variable symbol and store it `products_state`.


#TODO: Return the best solution's objective value and store it in `objective_value`.


print(f"Objective Value of the best solution: {objective_value}")
print(f"Products (at state 0): {products_state}")
