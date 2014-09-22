/*
 *** Auto generation by DataModel Tool, not edit. ***
 * DM Tool File  : @{toolversion}#
 * DataModel File: @{filename}#
 */
#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <stdlib.h>
#include "ftl_oam_id.h"
#include "ftl_oam_convert.h"


/*
 * @brief This function is to check the if INPUT parameters is null
 *
 *
 * @details
 *
 *     Function: null_char_pointer_check
 *
 *
 * @return
 *     0 -- No NULL Pointer; -1 -- Has NULL Pointer
 */

OAM_U32 null_char_pointer_check(char *arg, ...)
{
    va_list arg_list;
    char *para = NULL;
    OAM_S32 para_count = 0;
    OAM_U32 ret = 0x00;

    va_start(arg_list, arg);
    para = arg;

    for( ; para_count < __VA_MAX__; para_count ++)
    {
        if(!para)
        {
            printf("parameter[#%ld] is null\n", para_count);
            ret |= (1 << para_count);
        }
        para = va_arg(arg_list, char *);
        if(para && strcmp(para, __VA_MAGIC__) == 0)
        {
            break;
        }
    }
    va_end(arg_list);

    return ret;
}


/* Enum structure for oam value converting to protocol value */
FTL_OAM_CONVERT_t oam_convert_t[FTL_OAM_CONVERT_TABLE_MAX] = 
{
@{Oam_convert_table}#
};

/*
 * @brief This function is to convert the para value from oam value to protocol value
 *
 * @details
 *
 *     Function: ftl_oam_oam2protocol
 *
 *     Notes: While called in enodeb stack code, should avoid memory corruption.
 *            The fifth parameter "value" is OAM_U32(4 bytes) type pointer, but some
 *            global variables are U16(2 bytes). If these global variables are passed
 *            to this function directly, it will occur memory corruption. So we need
 *            to consider to do indirect passing and value convert.
 *
 *
 * @return
 *     0 -- Success; -1 -- Failure
 */
static OAM_S32 ftl_oam_oam2protocol(void *id, void *compare_id, OAM_S32 idlen, OAM_S32 string2int, OAM_U32 *value)
{
    OAM_S32 i = 0, j = 0;
    OAM_S32 ret = -1;
    OAM_S32 oam_value_int;
    OAM_U32 want_len = (!string2int) ? sizeof(OAM_U32) : idlen;
    char oam_value_string[idlen];

    ret = NULL_POINTER_CHECK((char *)id, (char *)compare_id, (char *)value);
    if(ret != 0)
    {
        return ret;
    }

    for(i = 0; i < sizeof(oam_convert_t) / sizeof(oam_convert_t[0]); i++)
    {
        if(oam_convert_t[i].id && oam_convert_t[i].id == compare_id)
        {
            *value = oam_convert_t[i].default_val;
            ret = ftl_oam_get(id, idlen, (!string2int) ? (void *)&oam_value_int : (void *)oam_value_string, &want_len);
            if(ret == FTL_OAM_RST_FAILURE)
            {
                break;
            }
            for(j = 0; j < sizeof(oam_convert_t[i].oam2protocol) / sizeof(oam_convert_t[i].oam2protocol[0]); j++)
            {
                if(((!string2int) ? oam_value_int : atoi(oam_value_string)) == oam_convert_t[i].oam2protocol[j].oam_val)
                {
                    *value = oam_convert_t[i].oam2protocol[j].protocol_val;
                    ret = 0;
                    break;
                }
            }
            break;
        }
    }

    return ret;
}


@{oam_get_fun}#
