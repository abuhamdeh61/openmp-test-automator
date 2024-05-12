#include <iostream>
#include <omp.h>
#include <iomanip>
using namespace std;

#define SIZE 700
#define MAX_ITER 700
#define THREAD_NUM 4

double grid[SIZE][SIZE];
void laplace_solver() {

    int i, j, iter;
    double diff, max_diff;
    #pragma omp parallel for schedule(runtime) 
    for (i = 0; i < SIZE; i++) {
        grid[i][0] = 1.0;
        grid[i][SIZE - 1] = 1.0;
        grid[0][i] = 0.0;
        grid[SIZE - 1][i] = 0.0;
    }
for (iter = 0; iter < MAX_ITER; iter++) {
        max_diff = 0.0;

        #pragma omp parallel for private(j, diff) reduction(max:max_diff) schedule(runtime) 
        for (i = 1; i < SIZE - 1; i++) {
            for (j = 1; j < SIZE - 1; j++) {
                diff = (grid[i-1][j] + grid[i+1][j] + grid[i][j-1] + grid[i][j+1]) / 4.0 - grid[i][j];
                grid[i][j] += diff;

                if (diff > max_diff)
                    max_diff = diff;
            }
        }

        // Check convergence
        if (max_diff < 1e-5)
            break;
    }

}

int main() {

    int i, j;

    double start_time = omp_get_wtime();
    laplace_solver();
    double end_time = omp_get_wtime();
    double execution_time = end_time - start_time;

    cout << execution_time << endl;

    // for (i = 0; i < SIZE; i++) {
    //     for (j = 0; j < SIZE; j++) {
    //         cout <<setw(10)<< grid[i][j] << " ";
    //     }
    //     cout << '\n';
    // }
    return 0;
}
