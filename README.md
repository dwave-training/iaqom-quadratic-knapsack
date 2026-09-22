[![Open in GitHub Codespaces](
  https://img.shields.io/badge/Open%20in%20GitHub%20Codespaces-333?logo=github)](
  https://codespaces.new/dwave-training/iaqom-quadratic-knapsack?quickstart=1)
  
# Quadratic Knapsack With the Stride<sup>TM</sup> Hybrid Solver

For the quadratic knapsack problem (QKP), convert the mathematical formulation into a model in Python. Use binary or set variables to represent the decision variable and code the problem so that it is compatible for submission to the Stride hybrid solver.

The objective is to maximize the total monetary value of products in the container. The decision variable represents which products are packed into the container. The constraint is that the total weight of selected products cannot exceed the container's weight limit.

Build the nonlinear model, define the objective function, and add the constraints.

In these exercises, the quadratic knapsack problem will be implemented using both a `for` loop and matrix multiplication, followed by a comparison of the results.

## Exercise 1: Model quadratic knapsack using binary variables with a for loop

This assignment explores the quadratic knapsack problem, in which the decision variable is represented using binary variables. The quadratic term of the objective function is formulated using a `for` loop.

Follow the instructions below, then submit the problem to the Stride solver.

Open `quadknapsack_binary_forloop_twomatrices.py`.

   1. Import the relevant package(s).

   2. Add the `pairwise_interaction` constant to the model object and name it `interaction_values`.
   
   3. Define the following quadratic objective using a `for` loop, and store it in `quadratic_obj`. Use the `sum()` function with a generator expression containing nested `for` clauses to calculate the interaction terms for all unique pairs of products. 

   ```math
   \sum_{i=0}^{n-1}\sum_{j=i+1}^{n-1}
   \left(
   \mathrm{interaction\_values}[i][j]
   \cdot \mathrm{products}[i]
   \cdot \mathrm{products}[j]
   \right)
   ```

   4. Set the objective function to maximize the total value of products in the container.

   5. Lock the model explicitly to prevent further changes.

   6. Instantiate the nonlinear sampler and name it `sampler`.
   
   7. Submit the nonlinear model to the Stride solver. Label your problem "Quadknap_binary_forloop_twomatrices" using the `label` parameter. The label is case-sensitive and uses an underscore. When you submit your problem, the label displays on your Leap dashboard.

   8. Return the best solution for the binary variable symbol and store it in `products_state`.

   9. Return the best solution's objective value and store it in `objective_value`.


## Exercise 2: Model quadratic knapsack using binary variables with matrix multiplication
In the second exercise, use binary variables and matrix multiplication instead of a `for` loop, and submit the problem to the Stride solver to obtain the best solution.

Follow the instructions below, then submit the problem to the Stride solver.

Open `quadknapsack_binary_matmul_twomatrices.py`.

   1. Import the relevant package(s).

   2. Define the half pairwise interaction matrix and name it `half_pairwise_interaction`.

   3. Add the constant `half_pairwise_interaction` to the model object and name it `interaction_values`.
   
   4. Define the quadratic objective using the `@` operator, and store it in `quadratic_obj`. 

   5. Set the objective function to maximize the total value of products in the container.

   6. Lock the model explicitly to prevent further changes.

   7. Instantiate the nonlinear sampler and name it `sampler`.
   
   8. Submit the nonlinear model to the Stride solver. Label your problem "Quadknap_binary_matmul_twomatrices" using the `label` parameter. The label is case-sensitive and uses an underscore. When you submit your problem, the label displays on your Leap dashboard.

   9. Return the best solution for the binary variable symbol and store it in `products_state`.

   10. Return the best solution's objective value and store it in `objective_value`.


## Example: Quadratic knapsack code with sets
The following example implements the quadratic knapsack problem using a set variable instead of
binary variables. Some parts of the code should look familiar from the model using binary variables; however,
there are some differences, particularly in how the objective function is structured. Here, matrix
multiplication is used to formulate the objective function, and the model is submitted to the Stride solver to obtain the best solution.

The code in the repo is intended to help you explore the model as part of the online course and, thus, does not contain any `TODO` sections.

Open `quadknapsack_set_matmul_onematrix.py` and follow along on the course page *Quadratic Knapsack Code With Sets*.
  