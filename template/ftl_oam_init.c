/*
 *** Auto generation by DataModel Tool, not edit. ***
 * DM Tool File  : @{toolversion}#
 * DataModel File: @{filename}#
 */
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <pthread.h>
#include "sname_def.h"
#include "ftl_oam_id.h"
#include "ftl_oam_init.h"


#define FTL_OAM_CONFIG_VERSION    "@{version}#"

struct FAPService_ FAPService;
static int inited = 0;
static pthread_rwlock_t rwlock;


void ftl_oam_get_xmlversion(char *buffer)
{
    if(buffer != NULL)
    {
        strncpy(buffer, (char*)FTL_OAM_CONFIG_VERSION, sizeof((char*)FTL_OAM_CONFIG_VERSION));
    }
}

int ftl_oam_dm_init(void)
{
    int i=0, j=0;
    char sname[512];
    char buf[1024];
    pthread_rwlockattr_t attr;

    pthread_rwlockattr_init(&attr);
    pthread_rwlockattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
    pthread_rwlock_init(&rwlock, &attr);
    pthread_rwlockattr_destroy(&attr);

    memset(&FAPService, 0, sizeof(FAPService));

    /* Init data here */
@{ftl_oam_dm_init}#
    inited = 1;

    return 0;
}

void ftl_oam_pm_reset_req_handler(void)
{

    /* reset pm parameter */
}

void ftl_oam_cm_update_req_handler(void)
{
    int i=0, j=0;
    char sname[512], buf[64];
    char value[64];


    /* update pm parameter */
@{ftl_oam_cm_update_req_handler}#

}

void ftl_oam_pm_update_req_handler(void)
{

    /* update pm parameter */
}

ftl_oam_rst_t ftl_oam_get(ftl_oam_id_t id, int idlen, void *buf, OAM_U32 *len)
{
    int len2copy;
    int w_flag = 0;

    if(!inited) {
        return FTL_OAM_RST_FAILURE;
    }

    if(buf == NULL || len == NULL) {
        return FTL_OAM_RST_FAILURE;
    }

    if(idlen != *len)
        w_flag = 1;

    len2copy = idlen < *len ? idlen : *len;

    memset(buf, 0, *len);
    pthread_rwlock_rdlock(&rwlock);
    memcpy(buf, id, len2copy);
    pthread_rwlock_unlock(&rwlock);
    *len = len2copy;

    return w_flag ? FTL_OAM_RST_LEN_NOT_MATCH : FTL_OAM_RST_SUCCESS;
}


ftl_oam_rst_t ftl_oam_set(ftl_oam_id_t id, int idlen, void *buf, OAM_U32 len)
{
    int len2copy = idlen < len ? idlen : len;
    int w_flag = 0;

    if(!inited) {
        return FTL_OAM_RST_FAILURE;
    }

    if(buf == NULL) {
        return FTL_OAM_RST_FAILURE;
    }

    if(idlen != len)
        w_flag = 1;

    pthread_rwlock_wrlock(&rwlock);
    memset(id, 0, idlen);/*XXX*/
    memcpy(id, buf, len2copy);
    pthread_rwlock_unlock(&rwlock);

    return w_flag ? FTL_OAM_RST_LEN_NOT_MATCH : FTL_OAM_RST_SUCCESS;
}
