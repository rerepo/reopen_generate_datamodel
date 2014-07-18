/*
 ============================================================================
 Name        : c-complie.c
 Author      : tmc9031@gmail.com
 Version     :
 Copyright   : Your copyright notice
 Description : Hello World in C, Ansi-style
 ============================================================================
 */

#include <stdio.h>
#include <stdlib.h>

#include "func.h"

//#include "oam/ftl_oam_id.h"
#include "sname_def.h"

int main(void) {

#if 0
    int i=0;    
    FTL_OAM_INC_VAL(i, 2);
    printf("FTL_OAM_INC_VAL=%d\n", i);
#endif

    printf("sname_def = %s\n", CM_SNAME_RootDataModelVersion);

	func();

	puts("!!!Hello World!!!"); /* prints !!!Hello World!!! */
	return EXIT_SUCCESS;
}
