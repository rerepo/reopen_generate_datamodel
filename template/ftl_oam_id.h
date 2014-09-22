/*
 * Copyright (c) 2010 SerComm Corporation. All Rights Reserved.
 *
 * SerComm Corporation reserves the right to make changes to this document
 * without notice. SerComm Corporation makes no warranty, representation or
 * guarantee regarding the suitability of its products for any particular
 * purpose. SerComm Corporation assumes no liability arising out of the
 * application or use of any product or circuit. SerComm Corporation
 * specifically disclaims any and all liability, including without limitation
 * consequential or incidental damages; neither does it convey any license
 * under its patent rights, nor the rights or others.
 */
/*
 *** Auto generation by DataModel Tool, not edit. ***
 * DM Tool File  : @{toolversion}#
 * DataModel File: @{filename}#
 */
#ifndef FTL_OAM_ID_H
#define FTL_OAM_ID_H

#include <stdint.h>
#include <stdbool.h>

#define FTL_OAM_STR_LEN (128)

typedef void* ftl_oam_id_t;

/*
 * Accroding to <SC-05-11-0209_LTE-Small-Cell-Data-Model_v3.18_20140114.xls>
 * All item marked with "exist" is defined.
 */
struct FAPService_ {
    struct {
    } TR098;
    struct {
    } TR104;
@{FAPService_OAM_Struct}#
};


extern struct FAPService_ FAPService;
@{OAM_typedef}#
@{OAM_Macro}#
typedef int ftl_oam_rst_t;

#define FTL_OAM_RST_LEN_NOT_MATCH    (1)
#define FTL_OAM_RST_SUCCESS          (0)
#define FTL_OAM_RST_FAILURE          (-1)

typedef enum ftl_oam_msgid {
    FTL_OAM_MSGID_PM_DATA_REQ = 1,
    FTL_OAM_MSGID_PM_DATA_CONF,
    FTL_OAM_MSGID_PM_DATA_RST,
    FTL_OAM_MSGID_PM_DATA_POST,
    FTL_OAM_MSGID_CM_DATA_REQ,
    FTL_OAM_MSGID_DM_DATA_RST
} ftl_oam_msgid_t;

/* Define oam data type to match with Radisys's data type.
 * If Radisys's data type change, we should also change 
 * here to keep synchronization.
 */
typedef unsigned long int OAM_U32;
typedef long int OAM_S32;

/* Add declaration by Phil Zhou */
ftl_oam_rst_t ftl_oam_get(ftl_oam_id_t id, int idlen, void *buf, OAM_U32 *len);
ftl_oam_rst_t ftl_oam_set(ftl_oam_id_t id, int idlen, void *buf, OAM_U32 len);

/*
* NOTE: You should only use these Macro to operate with OAM database item
*/
#define FTL_OAM_GET(ID, BUF, LEN)    ftl_oam_get(&ID, sizeof(ID), BUF, LEN)
#define FTL_OAM_SET(ID, BUF, LEN)    ftl_oam_set(&ID, sizeof(ID), BUF, LEN)
#define FTL_OAM_INC_VAL(ID, INC)    ({ ID += (INC); })
#define FTL_OAM_DEC_VAL(ID, DEC)    ({ ID -= (DEC); })



#endif /* FTL_OAM_ID_H */
