/**
 * @file tile.c
 * @brief Perform a blocked transpose
 * @author Adam Baumgartner
 * @date 9/20/25
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void blocked_transpose(double *input, double *output, int N, int B) {
    for (int ii = 0; ii < N; ii += B) {          // block row start
        for (int jj = 0; jj < N; jj += B) {      // block col start
            for (int i = ii; i < ii + B && i < N; i++) {
                for (int j = jj; j < jj + B && j < N; j++) {
                    output[j * N + i] = input[i * N + j];
                }
            }
        }
    }
}

void transpose(double *input, double *output, int N) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            output[j * N + i] = input[i * N + j];
        }
    }
}

void print_transpose(double *input, double *output, int N) {
    printf("Top-left 4x4 block of original matrix:\n");
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            printf("%6.1f ", input[i * N + j]);
        }
        printf("\n");
    }

    printf("Top-left 4x4 block of transposed matrix:\n");
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            printf("%6.1f ", output[i * N + j]);
        }
        printf("\n");
    }
}

int main(void) {
    int N = 1000;   // matrix dimension
    int B = 64;    // block size, pick based on cache calculation from part (a)

    // allocate matrices as flat arrays (row-major order)
    double *input  = malloc(N * N * sizeof(double));
    double *output_default = malloc(N * N * sizeof(double));
    double *output_tile = malloc(N * N * sizeof(double));

    // initialize input with some values
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            input[i * N + j] = (double)(i * N + j);
        }
    }

    clock_t start_time = clock(); // Clock Start
    // perform blocked transpose
    transpose(input, output_default, N);
    clock_t end_time_default = clock(); // Clock End
    // blocked_transpose(input, output_tile, N, B);
    clock_t end_time_tile = clock(); // Clock End

    //  Show the transpose results
    // print_transpose(input, output_default, N);
    // print_transpose(input, output_tile, N);

    // Display Runtime
    printf("default transpose: %.6f seconds\n", \
        (double)(end_time_default - start_time) /\
        CLOCKS_PER_SEC);

    printf("tile transpose: %.6f seconds\n", \
        (double)(end_time_tile - end_time_default) /\
        CLOCKS_PER_SEC);

    free(input);
    free(output_default);
    free(output_tile);
    return 0;
}
