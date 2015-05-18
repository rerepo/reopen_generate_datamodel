/*
 *** Auto generation by DataModel Tool, not edit. ***
 * DM Tool File  : @{toolversion}#
 * DataModel File: @{filename}#
 */
#include <string.h>
#include <sys/wait.h>
#include "parser.h"
#include "cgi_main.h"
#include "lca_fun_tab.h"
#include "lca_@{page}#.h"
#include "sname_def.h"
#include "lca_common.h"

extern int mylog(const char *format, ...);
extern int find_table_entry_index(char *index_list);

int action_@{page}#(LIST *head, int fileFunBase)
{
    char *thisfile, *nextfile, *action;
    char eMsg[512] = {0};
    int ret = 0;
#ifdef _SAMPLE_DEBUG_
    mylog("%s\n", __FUNCTION__);
#endif
    thisfile = find_val(head, "this_file");
    nextfile = find_val(head, "next_file");
    if(nextfile == NULL)
    {
        nextfile = thisfile;
    }
    action = find_val(head, "todo");

    if(action && strcmp(action, "save") == 0)
    {
        cgi_save_file(head, eMsg, &(cgi_fun_tab[fileFunBase]));
        ftl_commit();
        if(strlen(eMsg)){
            alert(eMsg, nextfile);
            return 0;
        }
    }
    else if(action && strcmp(action, "sync_config_femto_to_cmld") == 0)
    {
        ret = system("/ftl/bin/femto_cli sync_femto");
        if(WIFEXITED(ret))
        {
            strcpy(eMsg, "Warning:Sync config from femtolite to cmld fail");
            if(strlen(eMsg)){
                alert(eMsg, nextfile);
                return 0;
            }
        }
        sleep(2);
    }
    else if(action && strcmp(action, "addInstance") == 0)
    {
        action_add_instance(head);
        ftl_commit();
    }
    else if(action && strcmp(action, "delInstance") == 0)
    {
        action_del_instance(head);
        ftl_commit();
    }
    else if(action && strcmp(action, "modifyInstance") == 0)
    {
        action_modify_instance(head);
        ftl_commit();
    }
    html_parser(nextfile, head, cgi_fun_tab);
    return 0;
}
@{source_content}#
