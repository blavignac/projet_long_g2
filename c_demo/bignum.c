#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <gmp.h>
#include <time.h>

int main(int argc, char **argv){

    
    mpz_t num1;
    mpz_t num2;
    mpz_t result;
    mpz_init(result);
    
    mpz_init_set_str(num1, "1234567890123456789012345678901234567890",10);
    mpz_init_set_str(num2, "987654321987654321987654321987654321098",10);
    
    time_t start, end;
    double cpu_time_used;
    start = clock();

    mpz_mul(result, num1, num2);

    end = clock();
    cpu_time_used = ((double) (end - start)) / CLOCKS_PER_SEC;

    printf("Multiplication took %f seconds to execute \n", cpu_time_used);
    gmp_printf ("Result is an mpz %Zd\n", result);


}