#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <irq.h>
#include <libbase/uart.h>
#include <libbase/console.h>
#include <generated/csr.h>

int main(void)
{
#ifdef CONFIG_CPU_HAS_INTERRUPT
	irq_setmask(0);
	irq_setie(1);
#endif
	uart_init();
	printf("################################\n");
	printf("#####    My own program   ######\n");
	printf("################################\n\n");

	int taille = 32;
	char toom_cook [2];
	char a [taille];
	char b [taille];
	char ab [2*taille];

	while(1) {
		for (int i = 0; i < 2; i++){
			toom_cook[i]=uart_read();
		}

		for (int i = 0; i < taille; i++){
			a[i]=uart_read();
		}

		for (int i = 0; i < taille; i++){
			b[i]=uart_read();
		}
		
		controller_calc_toom_cook_write((uint32_t)strtol(toom_cook, NULL, 16));
		controller_calc_a_write((uint32_t)strtol(a, NULL, 16));
		controller_calc_b_write((uint32_t)strtol(b, NULL, 16));

		itoa(controller_calc_ab_read(), ab, 16);
		for (int i = 0; i < 2*taille; i++){
			uart_write(ab[i]);
		}	
	}

	return 0;
}
