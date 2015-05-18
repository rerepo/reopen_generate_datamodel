/*
 *** Auto generation by DataModel Tool, not edit. ***
 * DM Tool File  : @{toolversion}#
 * DataModel File: @{filename}#
 */

#include "ftl_oam_id.h"

#pragma once

#define __weak    __attribute__((weak))

#define __VA_MAGIC__ "Ser."

#define __VA_MAX__    (20)

#define NULL_POINTER_CHECK(...) \
    null_char_pointer_check(__VA_ARGS__, __VA_MAGIC__)

#define FTL_OAM_CONVERT_TABLE_MAX (200)
#define OAM2PROTOCOL_TABLE_MAX (64)

typedef struct
{
    OAM_S32 oam_val;
    OAM_U32 protocol_val;
}OAM2Protocol_t;

typedef struct
{
    void *id;
    OAM2Protocol_t oam2protocol[OAM2PROTOCOL_TABLE_MAX];
    OAM_U32 default_val;
}FTL_OAM_CONVERT_t;

OAM_U32 null_char_pointer_check(char *arg, ...);
@{oam_get_fun_head}#
