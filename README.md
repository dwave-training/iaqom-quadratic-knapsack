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


## Exercise 3: Model quadratic knapsack with sets
In the third exercise, use a set variable instead of binary variables. Some parts of the code should look familiar from the model using binary variables; however, there are some differences, particularly in how the objective function is structured. Here, matrix
multiplication is used to formulate the objective function, and the model is submitted to the Stride solver to obtain the best solution.

Follow the instructions below, then submit the problem to the Stride solver.

Open `quadknapsack_set_matmul_onematrix.py`.

   1. As you explore the starter code, notice two important differences: 
      -  A single `values_matrix` is used to represent the values of individual products and the interactions associated with selecting pairs of products together. In the earlier formulation, the `pairwise_interaction` matrix had zeros on the diagonal (because an item does not interact with itself), while the individual product values were stored separately in a one-dimensional array. Here, these two data structures are combined into one `values_matrix` where the diagonal entries are the values of individual products (linear values) and the off-diagonal entries are the pairwise added values (quadratic values).

      -  The NumPy `eye` function is used to create an identity matrix of dimensions `n x n`. It is stored in `identity_matrix`. This function returns a 2-D array with 1s on the diagonal and 0s elsewhere (also known as an identity matrix). The resulting matrix is added to the model as a constant, which will be used to build an indicator vector. You will need this for the objective function. Since a set is a dynamic array, its shape is not fixed, which has implications for the code.
   
   2. Define the set decision variable and store it in `products`. A set symbol is used to indicate the packed product indices (dynamic size 0 to `n`). Use `n` to determine the total number of elements in the set.

   3. Build a fixed-shape binary indicator vector of length `n` from the set and store it in `products_selected`. Use the `products` indices to select the corresponding rows of the identity matrix created above. Then, use `.sum(axis=0)` to add the selected rows column by column.
   The result `products_selected` is an indicator vector, where `products_selected[i] = 1` if item `i` is in the chosen set, and 0 otherwise. In other words, `products` stores the selected products as a set with non-fixed size, while `products_selected` provides another representation of that same selection but of a fixed length `n` where each position indicates whether the corresponding product is included in the set.

   4. Set the objective function, using the `@` operator, to maximize the total value of selected products. The row vector `products_selected`, `values`, and `products_selected` reshaped to a column vector are multiplied together, resulting in a single scalar value that represents the total value of the selected products. 

## Example: Quadratic Knapsack Comparison Script
This script is intended to serve as a hands-on illustration of how modeling choices (not just the underlying problem) can affect solver behavior and, thus, does not contain any TODO sections.

This script compares two formulations of the same quadratic knapsack problem:

- Binary formulation: each item is treated as a binary decision variable.
- Set formulation: the selected items are represented as a set.

The two formulations solve the exact same problem instance and should converge to the same optimal objective value. In practice, different problem input parameters can affect solution quality over time.

### Script overview

1. Generates a random quadratic knapsack instance with:
   - a symmetric interaction matrix for pairwise item values,
   - a vector of item weights,
   - a capacity determined by the total item weight.
2. Builds two optimization models for the same problem instance:
   - `build_binary_model(...)`
   - `build_set_model(...)`
3. Runs both formulations across a range of time limits and repeated samples.
4. Summarizes the objective values and saves a comparison plot.

### Main parameters to change

These are the main settings that affect the problem and the results. In practice, you usually only need to edit the values near the top of the script to explore different instances and solver behaviors.

| Parameter | What it does |
| --- | --- |
| `N` | Number of items. Larger values make the problem harder and slower. |
| `VALUE_LOW`, `VALUE_HIGH` | Range for off-diagonal interaction values. |
| `DIAG_LOW`, `DIAG_HIGH` | Range for diagonal values in the interaction matrix. |
| `ZERO_FRACTION` | Fraction of off-diagonal entries set to zero; higher values make the matrix sparser. |
| `WEIGHT_LOW`, `WEIGHT_HIGH` | Range for item weights. |
| `CAPACITY_FRACTION` | Knapsack capacity as a fraction of total weight. Smaller values create a tighter problem. |
| `TIME_LIMITS` | Solver time limits to compare. |
| `SAMPLES_PER_TIME` | Number of repeated runs per time limit. |

### Good experiments to try

- Change `N` to see how the formulations scale.
- Adjust `ZERO_FRACTION` to change matrix sparsity.
- Pick different values `CAPACITY_FRACTION` for a tighter knapsack constraint.
- Change `TIME_LIMITS` to compare performance more thoroughly.

Larger problem sizes and longer time limits can take a long time to run. For larger instances, it is best to keep the solver time limits at or below 30 seconds per run so the experiment remains practical.


### Output

The script prints:

- model size information for each formulation,
- summary tables of objective values by time limit,
- a plot comparing the binary and set formulations.

The output file is named:

```text
combined_solution_quality_time_n{N}_runs{SAMPLES_PER_TIME}.png
```
