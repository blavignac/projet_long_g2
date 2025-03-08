#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <gmp.h>

#define base_i 24
#define mask_0 ((uint64_t) 0b111111111111111111111111) 
#define mask_1 ((uint64_t) 0b111111111111111111111111 << 24) 
#define mask_2 ((uint64_t) 0b111111111111111111111111 << 48)

// base 24, ie: i = 24

int main(int argc, char **argv){
    printf("%d\n", argc);
    if( argc < 2    ){
        fprintf(stderr, "ERORR: Missing command line arguments (two positive integers around 2^60 in size)\n");
        return 1;
    }

    uint64_t num1, num2;

    sscanf(argv[1], "%llu", &num1);
    sscanf(argv[2], "%llu", &num2);
    printf("num1: %llu \nnum2: %llu \n", num1, num2);

    //Spliting the numbers in three parts (i.e toom-3)
    uint64_t m0 = num1 & mask_0;
    uint64_t n0 = num2 & mask_0;
    
    uint64_t m1 = (num1 & mask_1) >> base_i;
    uint64_t n1 = (num2 & mask_1) >> base_i;
    
    uint64_t m2 = (num1 & mask_2) >> (2 * base_i);
    uint64_t n2 = (num2 & mask_2) >> (2 * base_i);

    //Evaluating the polynomial at various points (0,1,-1,-2, +inf)
    int64_t p_0 = m0;
    int64_t q_0 = n0;
    
    int64_t p_1 = m0 + m1 + m2;
    int64_t q_1 = n0 + n1 + n2;
    
    int64_t p_m1 = (int64_t) m0 - ((int64_t) m1) + ((int64_t) m2);
    int64_t q_m1 = (int64_t) n0 - ((int64_t) n1) + ((int64_t) n2);
    
    int64_t p_m2 = (int64_t) m0 - ((int64_t) (m1 << 1)) + ((int64_t) (m2 << 2));
    int64_t q_m2 = (int64_t) n0 - ((int64_t) (n1 << 1)) + ((int64_t) (n2 << 2));
    
    int64_t p_inf = m2;
    int64_t q_inf = n2;
    
    //Multiplication point a point
    
    int64_t r_0 = p_0 * q_0;
    int64_t r_1 = p_1 * q_1;
    int64_t r_m1 = p_m1 * q_m1;
    int64_t r_m2 = p_m2 * q_m2;
    int64_t r_inf = p_inf * q_inf;
    
    //Interpolation (mul par l'inverse de la matrice) unsing bodrado sequence (less elementary operations)
    
    int64_t r0 = r_0;
    int64_t r4 = r_inf;
    int64_t r3 = (r_m2 - r_1);
    int64_t r1 = (r_1 - r_m1);
    int64_t r2 = r_m1 - r_0;
    
    r3 = ((3*r2 - r3) + 2*6*r_inf);// /6
    r2 = (2*r2 + r1 - 2*r4);// /2
    r1 = (3*r1 - 2*r3);// /6
    
    // Getting the final number by evaluatin the polinomial at our i, ie:24

    char* result = (char*) calloc(3, sizeof(int64_t)); 
    *((int64_t*) result) = (r0*6 + (r1 << base_i))/6;
    int64_t inter = (3*r2 + (r3 << base_i))/6;
    *((int64_t*) (((char*)result) + 6)) = *((int64_t*) (((char*)result) + 6)) + inter;
    *((int64_t*) (result + 12)) = *((int64_t*) (result + 12) + r4);
    
    printf("Product show as two 64 bits groups representing least significant bits(LSB) and most significant bits(MSB), in decimal for clarity, convert to binary and concat to have the value:\n LSB : %llu, MSB: %llu \n", *((uint64_t*)result), *(((uint64_t*)result) + 1));
    
    return 0;
}
