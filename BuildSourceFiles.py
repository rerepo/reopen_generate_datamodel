if __name__=='__main__':
    from cml import Cml
    from build import *
    import sys, getopt
    import os
    import codecs

    c = Cml()
    toolversion = '1.0.2'
    opts, args = getopt.getopt(sys.argv[1:], 'f:t:')
    for op, value in opts:
        if op == '-f':
            raw_file = value
        if op == '-t':
            template_dir = value
    c.load_file(raw_file)

    info = c.getElementsByUri('info')
    version = info.getAttribute('version')
    excel_filename = info.getAttribute('filename')

    
    current_path = os.getcwd()
    print(current_path)
    if not os.path.exists(current_path + '/output'):
        print('Create dictionary: output')
        os.makedirs(current_path + '/output')
    if not os.path.exists(current_path + '/output/htm'):
        print('Create dictionary: output/htm')
        os.makedirs(current_path + '/output/htm')
    if not os.path.exists(current_path + '/output/cgi'):
        print('Create dictionary: output/cgi')
        os.makedirs(current_path + '/output/cgi')
    if not os.path.exists(current_path + '/output/cgi/include'):
        print('Create dictionary: output/cgi/include')
        os.makedirs(current_path + '/output/cgi/include')
    if not os.path.exists(current_path + '/output/oam'):
        print('Create dictionary: output/oam')
        os.makedirs(current_path + '/output/oam')
    
    print('read web page name')
    pages = []

    find_web_page(c.getElementsByUri('Device'), pages)
    print(pages)


    # Create description.js
    res = 'var description = {\n'
    res += build_description(c.getElementsByUri('Device'), 'Device')
    # use as end flag
    res += '    "end": "end"\n'
    res += '}'
    output = codecs.open('output/htm/description.js', 'w', 'utf-8-sig')
    output.write(res)
    output.close()


    for page in pages:
        print('Create: ' + page + '.htm')
        template = open(template_dir + '/html.txt').read().replace('@{page}#', page)
        res, p = build_html(c.getElementsByUri('Device'), 'Device', page)
        template = template.replace('@{htm_content}#', res)
        res, p = build_html_hidden(c.getElementsByUri('Device'), 'Device', page)
        template = template.replace('@{htm_hidden}#', res)
        output = open('output/htm/' + page + '.htm', 'w')
        output.write(template)
        output.close()

    for page in pages:
        print('Create: lca_' + page + '.c')
        template = open(template_dir + '/action_fun.c', 'r').read().replace('@{version}#', version).replace('@{filename}#', excel_filename).replace('@{toolversion}#', toolversion)
        template = template.replace('@{page}#', page)
        res = build_CGI_source(c.getElementsByUri('Device'), 'Device', page)
        template = template.replace('@{source_content}#', res)
        output = open('output/cgi/lca_' + page + '.c', 'w')
        outlist = open('output/cgi/lca_list.mk', 'a')
        outlist.write('OBJS += lca_' + page + '.o' + '\r\n')
        output.write(template)
        output.close()
        outlist.close()

    for page in pages:
        print('Create: lca_' + page + '.h')
        template = open(template_dir + '/cgi_head_template.h', 'r').read().replace('@{version}#', version).replace('@{filename}#', excel_filename).replace('@{toolversion}#', toolversion)
        template = template.replace('@{page}#', page)
        res = build_CGI_head(c.getElementsByUri('Device'), 'Device', page)
        template = template.replace('@{head_content}#', res)
        list_header = open('output/cgi/include/lca_header.h', 'a')
        list_header.write('#include "lca_' + page + '.h"' + '\r\n')
        output = open('output/cgi/include/lca_' + page + '.h', 'w')
        output.write(template)
        output.close()
        list_header.close()


    # build lca_fun_tab_dm.h
    print('Create: lca_fun_tab_dm.h')
    template = ''
    for page in pages:
        template += '    {"page", KY_IS_FILE, NULL, NULL, action_page, \'5\', \'5\'},\n'.replace('page', page)
        template += build_fun_table(c.getElementsByUri('Device'), 'Device', page)
    output = open('output/cgi/include/lca_fun_tab_dm.h', 'w')
    output.write(template)
    output.close()

    # sname_def_dm.h
    res = build_sname_def(c.getElementsByUri('Device'), 'Device')
    output = open('sname_def_dm.h', 'w')
    output.write(res)
    output.close()

    # femto_default.xml
    print('Create: femto_default.xml')
    res = '<!-- data model version @{version}#-->\n'.replace('@{version}#', version)
    res += '<SERCOMM_CML>\n'
    res += build_femto_default_xml(c.getElementsByUri('Device'))
    res += '</SERCOMM_CML>\n'
    output = open('femto_default.xml', 'w')
    output.write(res)
    output.close()

    # OAM: ftl_oam_id.h
    print('Create: ftl_oam_id.h')
    template = open(template_dir + '/ftl_oam_id.h', 'r').read()
    template = template.replace('@{version}#', version).replace('@{filename}#', excel_filename).replace('@{toolversion}#', toolversion)
    res = build_oam_para_struct(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService', '    ', 1)
    template = template.replace('@{FAPService_OAM_Struct}#', res)
   
    res = build_oam_struct_typedef(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService' )
    template = template.replace('@{OAM_typedef}#', res)
    res = build_oam_macro(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService')
    template = template.replace('@{OAM_Macro}#', res)
    output = open('output/oam/ftl_oam_id.h', 'w')
    output.write(template)
    output.close()

    # OAM: ftl_oam_convert.h
    print('Create: ftl_oam_convert.h')
    template = open(template_dir + '/ftl_oam_convert.h', 'r').read()
    template = template.replace('@{version}#', version).replace('@{filename}#', excel_filename).replace('@{toolversion}#', toolversion)
    res = build_oam_get_fun_head(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService')
    template = template.replace('@{oam_get_fun_head}#', res)
    output = open('output/oam/ftl_oam_convert.h', 'w')
    output.write(template)
    output.close()
    # Clear OAM fun_name_arr for create ftl_oam_convert.c
    del fun_name_arr[:]

    # OAM: ftl_oam_convert.c
    print('Create: ftl_oam_convert.c')
    template = open(template_dir +  '/ftl_oam_convert.c', 'r').read()
    template = template.replace('@{version}#', version).replace('@{filename}#', excel_filename).replace('@{toolversion}#', toolversion)
    res = build_oam_convert_table(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService')
    template = template.replace('@{Oam_convert_table}#', res)
    res = build_oam_get_fun(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService' )
    template = template.replace('@{oam_get_fun}#', res) 
    output = open('output/oam/ftl_oam_convert.c', 'w')
    output.write(template)
    output.close()

    # OAM: ftl_oam_init.c
    print('Create: ftl_oam_init.c')
    template = open(template_dir + '/ftl_oam_init.c', 'r').read().replace('@{version}#', version).replace('@{filename}#', excel_filename).replace('@{toolversion}#', toolversion)
    res = build_oam_dm_init(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService')
    template = template.replace('@{ftl_oam_dm_init}#', res)
   
    res = build_oam_cm_update_req_handle(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService')
    template = template.replace('@{ftl_oam_cm_update_req_handler}#',res)
    output = open('output/oam/ftl_oam_init.c', 'w')
    output.write(template)

    output.close()

    # OAM: ftl_oam_init.h
    print('Create: ftl_oam_init.h')
    template = open(template_dir + '/ftl_oam_init.h', 'r').read()
    template = template.replace('@{version}#', version).replace('@{filename}#', excel_filename).replace('@{toolversion}#', toolversion)
    output = open('output/oam/ftl_oam_init.h', 'w')
    output.write(template)
    output.close()
