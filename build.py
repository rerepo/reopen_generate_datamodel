import re
import string

# these dictionary are used for store the code this tool generator

# Description : This function is used to find string from the array by dichotomization.
# Input : list, str
# Output : True/False
def oam_find(array, string):
    list_len = len(array)
    first_index = 0
    end_index = list_len - 1
    mid_index = 0
    if list_len == 0:
        array.insert(0, string)
        return False
    while first_index < end_index:
        mid_index =int((first_index + end_index)/2)
        if string > array[mid_index]:
            first_index = mid_index + 1
        elif string < array[mid_index]:
            end_index = mid_index - 1
        else:
            break
    if first_index == end_index:
        if array[first_index] > string:
            array.insert(first_index, string)
            return False
        elif array[first_index] < string:
            array.insert(first_index + 1, string)
            return False
        else:
            return True
    elif first_index > end_index:
        array.insert(first_index, string)
        return False
    else:
        return True

# Description : This funtion is uesed to compute the sname of the parameter
#
# Input : URI
# Ouput : sname
def get_sname_by_uri(uri):
    arr = uri.split('.')
    cgiName = '_'.join(arr)
    cgiName = cgiName.replace('Device_Services_FAPService_1', 'FAPService')
    cgiName = cgiName.replace('FAP_', '')
    cgiName = cgiName.replace('Device_X_SCM_EM', 'X_SCM_EM')
    cgiName = cgiName.replace('Device_Tunnel', 'Tunnel')

    return cgiName

# Description : this funtion is used to compute the SNAME MACRO, using the same
#              funtion to confirm CGI get the correct SNAME
# input :  URI (the full path of node)
# output : SNAME MACRO
def get_macro_by_uri(uri):
    arr = uri.split('.')
    index = ['i', 'j', 'k', 'l', 'm', 'n']
    
    p = 0
    for i in range(0, len(arr) - 1):
        if arr[i] == '0':
            arr[i] = index[p]
            p += 1
    if arr[1] == 'Services':
        i = 2
    else:
        i = 1
    macro = '_'.join(arr[i:]).replace('FAPService_1', 'FAPService').replace('FAP_', '')
    return 'CM_SNAME_' + macro

def get_oam_macro_by_uri(uri):
    #sname = get_macro_by_uri(uri)
    #return sname.replace('.', '_')
    num = 0
    #path = uri +  '.' + child.getAttribute('Name')
    res = ''
    arr = uri.split('.')
    for i in arr:
        if i == '0':
            num += 1
    macro = '_'.join(arr)
    res = macro.replace('_0', '').replace('Device_Services_', '')
    v = 'x,y,z'
    if num > 0:
        res += '(' + v[0:num*2-1] + ')'
    return res

def get_len_by_type(type_value):
    if len(type_value) is 0:
        return 0
    value = str(type_value)
    if value.lower().find('unsignedint') >= 0:
        return 11
    elif value.lower().find('int') >= 0:
        return 18
    elif value.lower().find('boolean') >= 0:
        return 4
    elif value.lower().find('DataTime') >= 0:
        return 256

    pattern = re.compile(r'\s*(\d+)\s*').search(value)
    if pattern is None:
        return 256
    else:
        return pattern.group()


# this function will generator a txtid for parameter
def get_txtid_by_uri(uri):
    return '_'.join(uri.split('.')).replace('_1_', '_').replace('_0_', '_')

def build_description(node, uri):
    res = ''

    for child in node.childNodes:
        name = child.getAttribute('Name')

        if child.getAttribute('Type') == 'object':

            # multi object
            if child.childNodes[0].getAttribute('Name') == '0':
                res += build_description(child, uri + '.' + name)
                continue
            res += build_description(child, uri + '.' + name)
        else:
            description = child.getAttribute("Description").replace('"', '\\"').replace("'", "\\'")
            if len(description) > 0:
                res += '    "' + get_txtid_by_uri(uri + '.' + name) + '"  :  "' + description + '",\n'
    return res


def find_web_page(node, dic):
    for child in node.childNodes:
        page = child.getAttribute('page')
        print(child.getAttribute('Name') + ' ' + page)

        if len(page) != 0 and  not page in dic:
            dic.append(page)
        if child.getAttribute('Type') == 'object':
            find_web_page(child, dic)



def build_get_fun(node, uri):
    cgiName = get_sname_by_uri(uri)
    page = node.getAttribute('page')

    getFun = 'int ' + page + '_get_'
    
    if node.getAttribute('Writeable') == '0':
        getFun += 'r_'

    elif str(node.getAttribute('Type')).find('boolean') >= 0:
        getFun += 'h_'

    getFun += cgiName + '(char *outbuf, LIST *head)\n'

    getFun += '{\n'
    if node.getAttribute('Type').lower().find('string') < 0:
        getFun += '    ftl_getNodeValue(CM_SNAME_' + cgiName.replace('Device_', '') + ', outbuf);\n'
        getFun += '    return 0;\n'
        getFun += '}\n'
        return getFun

    getFun += '    char strtmp[' + str(get_len_by_type(node.getAttribute('Type'))) + '] = "";\n'
    getFun += '    char *p = strtmp, *restr = outbuf;\n\n'
    getFun += '    ftl_getNodeValue(''CM_SNAME_' + cgiName.replace('Device_', '') + ', strtmp);\n'
    getFun += '    while(*p != \'\\0\')\n    {\n'
    getFun += '        if(*p == \'\\"\')\n'
    getFun += '            restr = strncat(restr, "&quot;", 6);\n'
    getFun += '        else\n'
    getFun += '            restr = strncat(restr, p, 1);\n'
    getFun += '        p++;\n    }\n'
    getFun += '    return 0;\n'
    getFun += '}\n'

    return getFun

def build_get_fun_head(node, uri):
    page = node.getAttribute('page')
    cgiName = get_sname_by_uri(uri)

    getFun = 'int ' + page + '_get_'
    
    if node.getAttribute('Writeable') == '0':
        getFun += 'r_'

    elif str(node.getAttribute('Type')).find('boolean') >= 0:
        getFun += 'h_'

    getFun += cgiName + '(char *outbuf, LIST *head);\n' 

    return getFun

def build_set_fun(node, uri):
    if node.getAttribute('Writeable') == '0':
        return ''
    name = node.getAttribute('Name')
    cgiName = get_sname_by_uri(uri)

    page = node.getAttribute('page')
    setFun = 'int ' + page + '_set_'

    if str(node.getAttribute('Type')).find('boolean') >= 0:
        setFun += 'h_'

    setFun += cgiName + '(char *value, char *eMsg, LIST *head)\n'


    #setFun = 'int ' + page + '_set_' + cgiName + '(char *value, char *eMsg, LIST *head)\n'
    setFun += '{\n'
    if cgiName == 'FAPService_AccessMgmt_set_FAPService_AccessMgmt_LTE_HNBName':
        setFun += '    COMMAND("/usr/sbin/ftl_cli_action.sh HNBName_check %s", value);\n'
        setFun += '    sleep(1);\n'
    elif cgiName == 'FAPService_CellConfig_set_FAPService_CellConfig_LTE_EPC_TAC':
        setFun += '    COMMAND("/usr/sbin/ftl_cli_action.sh TAC_check %s", value);\n'
        setFun += '    sleep(1);\n'
    setFun += '    if(0 != ftl_setValue(CM_SNAME_' + cgiName.replace('Device_', '') + ', value)){\n'
    setFun += '        sprintf(eMsg, "' + name + ' set value(%s) failure.\\\\n", value);\n'
    setFun += '        return CGI_WARNING;\n'
    setFun += '    }\n'
    setFun += '    return 0;\n'
    setFun += '}\n'

    return setFun

def build_set_fun_head(node, uri):
    if node.getAttribute('Writeable') == '0':
        return  ''

    name = node.getAttribute('Name')
    cgiName = get_sname_by_uri(uri)
    page = node.getAttribute('page')

    setFun = 'int ' + page + '_set_'
    if str(node.getAttribute('Type')).find('boolean') >= 0:
        setFun += 'h_'
    setFun += cgiName + '(char *value, char *eMsg, LIST *head);\n'
    return setFun

def getRangeByType(paraType):
    match = re.search(r'\[.*\]', paraType)
    if match:
        return match.group()
    else:
        return ''


def get_permission(node):
    permission = node.getAttribute('Permissions')
    if len(permission) == 0:
        return '0'
    else:
        return permission[0]


def build_input_text(child, uri, prev_permission='0'):
    html = ''
    cgiName = get_sname_by_uri(uri)

    permission = child.getAttribute('Permissions').strip()
    if len(permission) == 0:
        permission = '0'
    else:
        permission = permission[0]

    
    if permission != prev_permission :
        html += '$' + permission + '\n'

    # generator html text input 
    html += '    <tr class=r0 >\n'
    html += '        <td nowrap>' + \
            child.getAttribute('Name').replace('_SCM_', '_000E8F_') +\
            '</td>\n'
    html += '        <td wrap><input type="text" name="' + cgiName +\
            '" value="@' + cgiName + '#"'
    if len(child.getAttribute('Description')) > 0:
        html += ' txtid="' + get_txtid_by_uri(uri) + '"'
    if child.getAttribute('Writeable') == '0':
        html += ' readonly="readonly" style="border-style:none;"'
    html += ' size=15 maxlength=' + str(get_len_by_type(child.getAttribute('Type'))) + '>'+ getRangeByType(child.getAttribute('Type')) + '</td>\n'
    html += '    </tr>\n'

    return html


def build_input_checkbox(node, uri, prev_permission):
    permission = node.getAttribute('Permissions').strip()
    if len(permission) == 0:
        permission = '0'
    else:
        permission = permission[0]

    html = ''

    if permission != prev_permission:
        html = '$' + permission + '\n'

    cgiName = get_sname_by_uri(uri)
    html += '    <tr class=r0 >\n'
    html += '        <td nowrap>' +\
            node.getAttribute('Name').replace('_SCM_', '_000E8F_') +\
            '</td>\n'
    html += '        <td wrap><input type="checkbox" name="' + cgiName +\
            '" value="' + cgiName + '"'
    if node.getAttribute('Writeable') == '0':
        html += ' disabled="disabled"'
        
    html += '></td>\n'
    html += '    </tr>\n'

    return html


def build_hidden(node, uri, prev_permission):
    permission = node.getAttribute('Permissions').strip()
    if len(permission) == 0:
        permission = '0'
    else:
        permission = permission[0]

    hidden = ''
    if permission != prev_permission:
        hidden = '$' + permission + '\n'

    cgiName = get_sname_by_uri(uri)
    hidden += '    <input type="hidden" name="h_' + cgiName + '" value="@h_' + cgiName + '#">\n'

    return hidden


def build_table_list_fun(node, uri, page):
    cgiName = get_sname_by_uri(uri)
    getFun = 'int ' + page + '_get_' + cgiName + '_list(char *outbuf, LIST *head)\n';
    getFun += '{\n';
    getFun += '    return build_list_html(outbuf, "' + uri + '.' + '");\n'
    getFun += '}\n'
    return getFun

def build_table_list_fun_head(node, uri, page):
    cgiName = get_sname_by_uri(uri)
    getFun = '\nint ' + page + '_get_' + cgiName + '_list(char *output, LIST *head);\n';
    return getFun

# this funtion will string which store the html context
def build_title(node, uri, prev_permission='0'):

    permission = node.getAttribute('Permissions').strip()
    if len(permission) == 0:
        permission = '0'
    else:
        permission = permission[0]

    html = ''
    if permission != prev_permission:
        html += '$' + permission + '\n'

    '''
    # if the child node of this node is 'object' , we do't need display
    # the Name of this node in the Web, just skip it, but the permission 
    # of this node may be useful, so also return it
    if node.childNodes[0].getAttribute('Type') == 'object':
        return permission
    '''

    title = (uri + '.' + node.getAttribute('Name')).replace('.', '_').replace('_SCM_', '_000E8F_').replace('.', '_').replace('Device_Services_', '').replace('FAPService_1_', 'FAPService_')
    html += '    <tr class=r0 >\n'
    html += '        <td width="170" colspan="2" nowrap class="th_color">' + title + '</td>\n'
    html += '    </tr>\n'

    return html


def build_table_list(node, uri, prev_permission='0'):
    permission = get_permission(node)
    html = ''
    if permission != prev_permission:
        html += '$' + permission

    html += '@' + get_sname_by_uri(uri) +  '#\n'
    return html


# this funtion will return a tuple
# first item is the html content
# secont item is the permission
def build_html(node, uri, page, prev_permission='0'):
    res = ''
    permission = prev_permission
    for child in node.childNodes:
        name = child.getAttribute('Name')
      
       
        if child.getAttribute('Type') == 'object':

            if child.getAttribute('page') == page:
                # multi object
                if child.childNodes[0].getAttribute('Name') == '0':
                    # multi object
                    res += build_table_list(child, uri + '.' + name, permission)
                    permission = get_permission(child)
                    continue
                # we need print a title and update the permission
                if child.childNodes[0].getAttribute('Type') != 'object':
                    res += build_title(child, uri, permission)
                    permission = child.getAttribute('Permissions').strip()
                    if len(permission) == 0:
                        permission = '0'
                    else:
                        permission = permission[0]

            tmp, permission = build_html(child, uri + '.' + name, page, permission)
            res += tmp

        else:
            if child.getAttribute('page') != page:
                continue
           
            if child.getAttribute('Type').lower() == 'boolean':
                res += build_input_checkbox(child, uri + '.' + name, permission)
            else:
                res += build_input_text(child, uri + '.' + name, permission)

            # Update the permission
            permission = child.getAttribute('Permissions').strip()
            if len(permission) == 0:
                permission = '0'
            else:
                permission = permission[0]
    return res, permission


def build_CGI_source(node, uri, page):
    res = ''
    for child in node.childNodes:
        name = child.getAttribute('Name')

        if child.getAttribute('Type') == 'object':

            # it look need build table list cgi for multi object
            #if name == '0':
            #    break
            if child.childNodes[0].getAttribute('Name') == '0' and child.getAttribute('page') == page:
                res += build_table_list_fun(child, uri + '.' + name, page)
                continue
            
            res += build_CGI_source(child, uri + '.' + name, page)
        else:
            if child.getAttribute('page') == page:
                res += build_get_fun(child, uri + '.' + name)
                res += build_set_fun(child, uri + '.' + name)
    
    return res


def build_CGI_head(node, uri, page):
    res = ''

    for child in node.childNodes:
        name = child.getAttribute('Name')

        if child.getAttribute('Type') == 'object':

            if child.childNodes[0].getAttribute('Name') == '0' and child.getAttribute('page') == page:
                res += build_table_list_fun_head(child, uri + '.' + name, page)
                continue

            res += build_CGI_head(child, uri + '.' + name, page)
        else:
            if child.getAttribute('page') == page:
                res += build_get_fun_head(child, uri + '.' + name)
                res += build_set_fun_head(child, uri + '.' + name)
    
    return res



def build_html_hidden(node, uri, page, prev_permission='0'):
    res = ''
    permission = prev_permission
    for child in node.childNodes:
        name = child.getAttribute('Name')

        if child.getAttribute('Type') == 'object':
            if name == '0':
                #
                break
            else:
                tmp, permission = build_html_hidden(child, uri + '.' + name, page, permission)
                res += tmp
        else:
            if child.getAttribute('page') != page:
                continue
            if child.getAttribute('Type') == 'boolean':
                res += build_hidden(child, uri + '.' + name, permission)
                permission = child.getAttribute('Permissions')
                if len(permission) == 0:
                    permission = '0'
                else:
                    permission = permission[0]
    return res, permission

def build_cgi_set_fun(node, uri, page):
    res = ''

    for child in node.childNodes:
        name = child.getAttribute('Name')
        if child.getAttribute('Type') == 'object':
            if name == '0':
                pass
            else:
                res += build_cgi_set_fun(child, uri + '.' + name, page)
        else:
            if child.getAttribute('page') != page:
                continue

            res += build_set_fun(node, uri + '.' + name)

    return res

def build_cgi_set_fun_head(node, uri):
    res = ''
    for child in node.getAttribute('Name'):
        name = child.getAttribute('Name')
        if child.getAttribute('Type') == 'object':
            if name == '0':
                break
            else:
                res +=  build_cgi_set_fun_head(child, uri + '.' + name)
        else:
            if child.getAttribute('para') != page:
                continue

            res += build_set_fun_head(uri + '.' + name)
    return res

def build_cgi_get_fun(node, uri):
    res = ''

    for child in node.childNodes:
        name = child.getAttribute('Name')
        if child.getAttribute('Type') == 'object':
            if name == '0':
                break
            else:
                res += build_cgi_get_fun(child, uri + '.' + name, page)
        else:

            if child.getAttribute('page') != page:
                continue
            res += build_get_fun(node, uri + '.' + name)
    return res


def build_cgi_get_fun_head(node, uri):
    res = ''

    for child in node.childNodes:
        name = child.getAttribute('Name')
        if child.getAttribute('Type') == 'object':
            if name == '0':
                break
            else:
                res += build_cgi_get_fun_head(child, uri + '.' + name)
        else:
            if child.getAttribute('page') != page:
                continue
            res += build_get_fun_head(child, uri + '.' + name)
    return res

def build_fun_table(node, uri, page):
    res = ''

    for child in node.childNodes:
        name = child.getAttribute('Name')
        paraType = child.getAttribute('Type')

        if child.getAttribute('Type') == 'object':

            if child.childNodes[0].getAttribute('Name') == '0' and child.getAttribute('page') == page:
                cgiName = get_sname_by_uri(uri + '.' + name)
                res += '    {"' + cgiName + '" , KY_IS_VAR, ' + page + '_get_' + cgiName
                res += "_list, NULL, NULL, '7', '7'},\n"
            else:
                res += build_fun_table(child, uri + '.' + name, page)
        else:
            if child.getAttribute('page') != page:
                continue

            cgiName = get_sname_by_uri(uri + '.' + name)
            res += '    {"' 
            if paraType == 'boolean':
                res += 'h_'
            res += cgiName + '", KY_IS_VAR, ' + page + '_get_'

            if child.getAttribute('Writeable') == '0':
                res += 'r_'
            elif paraType == 'boolean':
                res += 'h_'
            res += cgiName 
            res += ', '

            if child.getAttribute('Writeable') == '0':
                res += 'NULL, '
            else:
                res += page + '_set_'
                if paraType == 'boolean':
                    res += 'h_'
                res += cgiName + ', '
            res += 'NULL, '

            permission = child.getAttribute('Permissions')
            if len(permission) == 0:
                permission = '0,0'

            res += "'" + permission[0] + "', '" + permission[2] +"'},\n"
    return res

def build_action_fun(page):
    f = open('action_fun.c')
    fun_str = f.read().replace('#{page}', page)
    return fun_str

def save_file(webfiles, cgi_source, cgi_header):
    for page in webfiles.keys():
        f = open('output/' + page+'.htm', 'w')
        f.write(webfiles[page]['html'])
        f.close()
        #print(page)
        #print(webfiles[page]['html'])
    for page in cgi_source.keys():
        f = open('output/lca_' + page + '.c', 'w')
        f.write(build_action_fun(page))
        f.write(cgi_source[page])
        f.close
        f = open('output/lca_' + page + '.h', 'w')
        f.write(cgi_header[page])
        f.close()

def build_sname_def(node, uri):
    index = ['i', 'j', 'k', 'l']
    res = ''
    for child in node.childNodes:
        arr = (uri + '.' + child.getAttribute('Name')).split('.')
        if arr[-1] == '0':
            sname = '.'.join(arr[0:-1]).replace('.0.', '.%d.')
        else:
            sname = '.'.join(arr).replace('.0.', '.%d.')
        
        p = 0
        for i in range(0, len(arr) - 1):
            if arr[i] == '0':
                arr[i] = index[p]
                p += 1
        if arr[1] == 'Services':
            i = 2
        else:
            i = 1

        if child.getAttribute('Type') == 'object':
            if not child.getAttribute('Name') == '0':
                res += build_sname_def(child, uri + '.' + child.getAttribute('Name'))
                continue
            if arr[-1] == '0':
                del arr[-1]
            macro = '_'.join(arr[i:]).replace('FAPService_1', 'FAPService').replace('FAP_', '')

            res += '#define CM_SNAME_' + macro + '_Table '
            blank = 71 - len(macro) - 18
            if blank > 0:
                for k in range(1, blank):
                    res += ' '
            res += '    "' + sname + '."\n'
            res += build_sname_def(child, uri + '.' + child.getAttribute('Name'))
            break
        else:
            macro = '_'.join(arr[i:])
            macro = macro.replace('FAPService_1', 'FAPService')
            macro = macro.replace('FAP_', '')

            res += '#define CM_SNAME_' + macro
            blank = 78 - len(macro) - 18
            if blank > 0:
                for k in range(1, blank):
                    res += ' '
            res += '    "' + sname + '"\n'

    return res

def build_femto_default_xml(node):
    xml_str = '<Element Name="' + node.getAttribute('Name') + '." ' 
    if node.getAttribute('Writeable') == '1':
        xml_str += 'Writable="1" '
    #xml_str += 'deviceModel="TDFAP" '
    xml_str += 'DataType="object"'
    if len(str(node.getAttribute('Permissions')).strip()) > 0:
        xml_str += ' Permissions="' + node.getAttribute('Permissions') + '"'
    if len(str(node.getAttribute('SaveType'))) > 0:
        xml_str += ' SaveType="' + node.getAttribute('SaveType') + '"'
    xml_str += '>\n' 
    for child in node.childNodes:
        if child.getAttribute('Type') == 'object':
            xml_str += build_femto_default_xml(child)
        else:
            xml_str += '<Element Name="' + child.getAttribute('Name') + '"'
            if child.getAttribute('Writeable') == '1':
                xml_str += ' Writable="1"'
            xml_str += ' deviceModel="TDFAP"'

            if len(child.getAttribute('NotifyMode')) == 0:
                xml_str += ' notifyMode="Off"'
            else:
                xml_str += ' notifyMode="' + child.getAttribute('NotifyMode') + '"'
            if not len(child.getAttribute('denyActive')) == 0:
                xml_str += ' denyActive="' + child.getAttribute('denyActive') + '"'
            child.setAttribute('Value', child.getAttribute('Value'))
            if str(child.getAttribute('Type')).lower().find('Int') >= 0:
                xml_str += ' value="' + str(int(str(child.getAttribute('Value')))).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", '&apos;').replace('"', '&quot;') +'" '
            else:
                xml_str += ' value="' + str(child.getAttribute('Value')).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace("'", '&apos;').replace('"', '&quot;') + '" '

            xml_str += 'DataType="' + child.getAttribute('Type').replace(' ', '') + '"'
            if len(str(child.getAttribute('SaveType'))) > 0:
                xml_str += ' SaveType="' + child.getAttribute('SaveType') + '"'
            if len(str(child.getAttribute('Permissions'))) > 0:
                xml_str += ' Permissions="' + child.getAttribute('Permissions') + '"'
            xml_str += '></Element>\n'
    xml_str += '</Element>\n'
    return xml_str

def checkEumeData(enumData):
    enumCheck = 0
    if not len(enumData) == 0:
        #if re.compile('[-]\d+\$').match(enumData.split(',')[0]) :
        #if enumData.split(',')[0][1:].isdigit():
        if enumData.split(',')[0].strip().isdigit():
            enumCheck = 1
        elif enumData.split(',')[0].strip()[1:].isdigit():
            enumCheck = 1
    return enumCheck
# File: ftl_oam_convert.c 
# funtion: get function
# ftl_oam_get(void name, ...)
fun_name_arr = {'tds':[], 'lte':[]}
def build_oam_get_fun(project, node, uri):
    global fun_name_arr
    res = ''
    support=''
    if project == 'lte':
        support='F'
    if project == 'tds':
        support='T'
    for child in node.childNodes:
        name = child.getAttribute('Name')
        paraType = child.getAttribute('Type').lower()
        if not child.getAttribute('Support') == support and not child.getAttribute('Support') == 'C':
            continue
        if child.getAttribute('Type') == 'object':
            res += build_oam_get_fun(project, child, uri + '.' + name)
            if name == '0':
                return res
        else:
            #fun_name = get_oam_macro_by_uri(uri + '.' + name)
            arr = (uri + '.' + name).split('.')
            if arr[-2] == '0':
                #fun_name = arr[-3] + '_' + arr[len(arr) - 1]
                fun_name = '_'.join(arr[-3:])
            else:
                fun_name = '_'.join(arr[-2:])

            # check fun_name is repetition or not    
            Is_repetition = oam_find(fun_name_arr[project], fun_name)
            if Is_repetition == True:
                if arr[-2] == '0':
                    fun_name = '_'.join(arr[-4:])
                else:
                    fun_name = '_'.join(arr[-3:])

            oam_macro = get_oam_macro_by_uri(uri + '.' + name)
            # comment
            res += '/*\n *@brief This function is to convert the para value from oam value to protocol value\n'
            res += ' *\n * @details\n *\n'
            res += ' *    Function :ftl_oam_get_' + fun_name + '\n'
            res += ' *\n *    Notes:While called in enodeb stack code, should avoid memory corruption.\n'
            res += ' *          The first parameter of this function is OAM_U32 type pointer, but some \n'
            res += ' *          global variables are U16. If these globa variables are passed to this function\n'
            res += ' *          directly, it will occur memory corruption. So we need to consider to do indirect\n'
            res += ' *          passing and value convert.\n'
            res += ' *\n *\n * @return\n'
            res += ' *     0 -- Success; -1 -- Failure\n */\n'
            res += '__weak OAM_S32 ftl_oam_get_' + fun_name 
            enumData = child.getAttribute('EnumData').strip()

            enumCheck = checkEumeData(enumData)
            if enumCheck == 1:
                res += '(OAM_U32 *' + name + '_val'
            else:
                res += '(void *' + name + '_val, OAM_U32 *length'

            if oam_macro[-3:] == '(x)':
                res += ', OAM_U32 Index)\n'
            elif oam_macro[-5:] == '(x,y)':
                res += ', OAM_U32 Index_x, OAM_U32 Index_y)\n'
            else:
                res += ')\n'
            res += '{\n'
            res += '    OAM_S32 ret = 0; \n\n'
            res += '    ret = NULL_POINTER_CHECK((char *) ' + name + '_val);\n'
            res += '    if(ret != 0)\n'
            res += '    {\n'
            res += '        return ret;\n'
            res += '    }\n\n'
            #if not len(enumData) == 0:
            #if paraType.find('int') >= 0 and not len(enumData) == 0:
            if enumCheck == 1:
                arr = enumData.split(',')
                default = child.getAttribute('Value')
                value_id = 0
                for i in range(0, len(arr)):
                    if arr[i].strip() == default:
                        value_id = i
                        break
                res += '    return ftl_oam_oam2protocol(&' + get_oam_macro_by_uri(uri + '.' + name).replace('(x)', '(Index)').replace('(x,y)', '(Index_x, Index_y)') + ',' +\
                    ' &' + get_oam_macro_by_uri(uri + '.' + name).replace('(x)', '(1)') +',' + \
                    ' sizeof(' + get_oam_macro_by_uri(uri + '.' + name).replace('(x)', '(Index)') +'),'
                if paraType.find('string') >= 0:
                    res += ' 1' + ', ' + name + '_val);\n'
                else:
                    res += ' 0' + ', ' + name + '_val);\n'

            else:
                res += '    return FTL_OAM_GET(' +  get_oam_macro_by_uri(uri + '.' + name).replace('(x)', '(Index)').replace('(x,y)', '(Index_x, Index_y)') +\
                    ', ' + name + '_val, length);\n'
            res += '}\n\n'
    return res

# this Funtion will generator code Get Fun Head file and emue data
def build_oam_get_fun_head(project, node, uri, dic=[]):
    global fun_name_arr
    res = ''
    support=''
    if project == 'lte':
        support='F'
    if project == 'tds':
        support='T'
    for child in node.childNodes:
        name = child.getAttribute('Name')
        paraType = child.getAttribute('Type').lower()
        if not child.getAttribute('Support') == support and not child.getAttribute('Support') == 'C':
            continue
        if child.getAttribute('Type') == 'object':

            res += build_oam_get_fun_head(project, child, uri + '.' + child.getAttribute('Name'), dic)
            if name == '0':
                break
        else:
            arr = (uri + '.' + name).split('.')
            if arr[-2] == '0':
                #fun_name = arr[-3] + '_' + arr[len(arr) - 1]
                fun_name = '_'.join(arr[-3:])
            else:
                fun_name = '_'.join(arr[-2:])
            # check fun_name is repetition or not    
            Is_repetition = oam_find(fun_name_arr[project], fun_name)
            if Is_repetition == True:
                if arr[-2] == '0':
                    fun_name = '_'.join(arr[-4:])
                else:
                    fun_name = '_'.join(arr[-3:])

            oam_macro = get_oam_macro_by_uri(uri + '.' + name)
            #print(oamMacro[-3:])
            enumData = child.getAttribute('EnumData').strip()

            enumCheck = checkEumeData(enumData)
            if enumCheck == 1:
                res += 'OAM_S32 ftl_oam_get_' + fun_name
                res += '(OAM_U32 *' + name + '_val'
            else:
                res += 'OAM_S32 ftl_oam_get_' + fun_name
                res += '(void *' + name + '_val, OAM_U32 *length'

            if oam_macro[-3:] == '(x)':
                res += ', OAM_U32 Index);\n'
            elif oam_macro[-5:] == '(x,y)':
                res += ', OAM_U32 Index_x, OAM_U32 Index_y);\n'
            else:
                res += ');\n'
            if enumCheck == 1 and not name in dic:
                dic.append(name)
                res += '\ntypedef enum\n{\n'
                arr = enumData.split(',')
                for i in arr:
                    i = i.strip()
                    res += '    ' + name + '_' + i.replace('-', 'minus') + ' = ' + i + ',\n'
                res += '}' + name + '_e;\n\n'
                
    return res

def build_oam_convert_table(project, node, uri):
    res = ''
    support=''
    if project == 'lte':
        support='F'
    if project == 'tds':
        support='T'
    for child in node.childNodes:
        if not child.getAttribute('Support') == support and not child.getAttribute('Support') == 'C':
            continue
        name = child.getAttribute('Name')
        if child.getAttribute('Type') == 'object':
            res += build_oam_convert_table(project, child, uri + '.' + name)
            if name == '0':
                break
        else:

            enumData = child.getAttribute('EnumData')
            if checkEumeData(enumData) == 0:
                continue
            if len(enumData) == 0:
                continue
            enum_arr = enumData.split(',')
            res += '    {\n'
            res += add_indent('    ', 2) + '&' + get_oam_macro_by_uri(uri + '.' + name).replace('(x)', '(1)') + ',\n        {\n'
            value = child.getAttribute('Value')
            index = 0

            for i in range(0, len(enum_arr)):
                if str(value).strip() == str(enum_arr[i]).strip():
                    index = i
                enum_arr[i] = enum_arr[i].strip()
                if enum_arr[i][0] == '-':
                    enum_arr[i] = 'minus' + enum_arr[i][1:]
                res += add_indent('    ', 3) + '{' + name + '_' + str(enum_arr[i]).strip() + ', ' + str(i) + '},\n'
            res += '        },\n'
            res += '        ' + str(index) + '\n'
            res += '    },\n'
    return res

def add_indent(indent, num):
    return ''.join(list(map(lambda x: indent, range(1, num + 1))))

def computeMaxNum(node, name):
    for child in node.childNodes:
        childname = child.getAttribute('Name')
        if childname.find(name) >= 0 and childname.find('Max') > 0 and childname.find('Entries') > 0:
            value = child.getAttribute('Value')
            if len(value) is None:
                return '32'
            else:
                return value
    return '32'

def find_sm(project, node):
    rt=0
    support=''
    if project == 'lte':
        support='F'
    if project == 'tds':
        support='T'
    for child in node.childNodes:
        if not child.getAttribute('Support') == support and not child.getAttribute('Support') == 'C':
            continue
        saveType = child.getAttribute('SaveType')
        if saveType == 'SM' or saveType == 'HM':
            rt=1
            break
    return rt

def build_oam_para_struct(project, node, uri, indent, num=0):
    res=''
    support=''
    if project == 'lte':
        support='F'
    if project == 'tds':
        support='T'
    
    for child in node.childNodes:
        if not child.getAttribute('Support') == support and not child.getAttribute('Support') == 'C':
            continue
        name = child.getAttribute('Name')
        paraType = child.getAttribute('Type')

        if paraType == 'object':

            # For multi object '0' node is used as template to generator struct code,
            # other instance list like '1', '2' ... , will be ignored
            if name == '0':
                res += build_oam_para_struct(project, child, uri + '.' + name, indent, num)
                break

            res += add_indent(indent, num) + 'struct '
            res += get_oam_macro_by_uri(uri + '.' + name).replace('(x)', '')
            res += ' {\n'
         
            # add __dirty and __par into struct
            if child.childNodes[0].getAttribute('Name') == '0':
                sm = find_sm(project, child.childNodes[0])
            else:
                sm = find_sm(project, child)
            if sm == 1:
                res += add_indent(indent, num + 1)
                res += 'int             __dirty;\n'
                res += add_indent(indent, num + 1)
                res += 'void*           __par;\n' 
            
            res += build_oam_para_struct(project, child, uri + '.' + name, indent, num + 1)
            res += add_indent(indent, num)
            if child.childNodes[0].getAttribute('Name') == '0':
                res += '} ' + name + '[' + \
                        computeMaxNum(node, name) + '];\n'
            else:
                res += '} ' + child.getAttribute('Name') + ';\n'
        elif paraType == 'boolean':
            res += add_indent(indent, num)
            res += 'bool            ' + child.getAttribute('Name') + ';\n'
        elif paraType.find('int') == 0:
            res += add_indent(indent, num)
            res += 'int             ' + child.getAttribute('Name') + ';\n'
        elif paraType.lower().find('unsignedint') == 0:
            res += add_indent(indent, num)
            res += 'unsigned int    ' + child.getAttribute('Name') + ';\n'
        elif paraType.find('string') >= 0:
            res += add_indent(indent, num)
            res += 'char            ' + child.getAttribute('Name') + '[' + str(get_len_by_type(child.getAttribute('Type'))) + '];\n'
        elif paraType.find('dateTime') >= 0:
            res += add_indent(indent, num)
            res += 'char            ' + name + '[256];\n'
    return res

def build_oam_struct_typedef(project, node, uri):
    res = ''
    support=''
    if project == 'lte':
        support='F'
    if project == 'tds':
        support='T'
    for child in node.childNodes:
        if not child.getAttribute('Support') == support and not child.getAttribute('Support') == 'C':
            continue
        name = child.getAttribute('Name')
        if child.getAttribute('Type') == 'object':
            if name == '0':
                res += build_oam_struct_typedef(project, child, uri + '.' + name)
                return res
            oamMacro = get_oam_macro_by_uri(uri + '.' + name)
            space_len = 150 - len(oamMacro)
            res += 'typedef struct ' + oamMacro + ' '
            for i in range(1, space_len):
                res += ' '
            res +=  oamMacro + '_t;\n'
            res += build_oam_struct_typedef(project, child, uri + '.' + name).replace('(x)', '');
        else:
            '''
            oamMacro = get_oam_macro_by_uri(uri + '.' + name)
            space_len = 80- len(oamMacro)
            res += 'typedef struct '  + oamMacro
            for i in range(1, space_len):
                res += ' '
            res += oamMacro + '_t\n'
            '''
    return res

def build_kpi_macro(project, node, uri):
    value=''
    res=''
    mr_flag = 0
    if uri.find('Device.PeriodicStatistics.SampleSet.3.Parameter') >= 0:
        mr_flag = 1
    for child in node.childNodes:
        arr = (uri + '.' + child.getAttribute('Name')).split('.')
        if child.getAttribute('Type') == 'object' and not child.getAttribute('Name') == '0':
            res += build_kpi_macro(project, child, uri + '.' + child.getAttribute('Name'))
        if child.getAttribute('Name') == 'X_SCM_Name' and not len(child.getAttribute('Value')) == 0:
            value = child.getAttribute('Value')
            if mr_flag == 1:
                macro = project.upper() + '_' + (value + ' ').upper().replace('.', '_')
            else:
                macro = project.upper() + '_KPI_' + (value + ' ').upper().replace('.', '_')
            sname = uri + '.' + 'Values'
            res += '#define ' + macro + ' '
            space_len = 150 - len(macro)
            for i in range(1, space_len):
                res += ' '
            res += '"' + sname + '"\n'
            macro = project.upper() + '_' + value.upper().replace('.', '_') + '_ENABLE'
            sname = uri + '.' + 'Enable'
            res += '#define ' + macro + ' '
            space_len = 150 - len(macro)
            for i in range(1, space_len):
                res += ' '
            res += '"' + sname + '"\n'
    return res

def build_oam_macro(project, node, uri):
    key = ['x', 'y', 'z']
    res  = ''
    support=''
    if project == 'lte':
        support='F'
    if project == 'tds':
        support='T'
    for child in node.childNodes: 
        name = child.getAttribute('Name')
        if not child.getAttribute('Support') == support and not child.getAttribute('Support') == 'C':
            continue

        if len(child.childNodes) > 0 and child.childNodes[0].getAttribute('Name') == '0':
            res += build_oam_macro(project, child, uri + '.' + name)
            continue

        macro = get_oam_macro_by_uri(uri + '.' + name)
        res += '#define ' + macro + ' '
        space_len = 150 - len(macro)
        for i in range(1, space_len):
            res += ' '

        macro = ''
        num = 0
        arr = (uri + '.' + name).split('.')
        if arr[0] == 'Device':
            del arr[0]
        if arr[0] == 'Services':
            del arr[0]
        for i in arr:
            if i == '0':
                macro += '[(' + key[num] +')-1]'
                num += 1
            else:
                macro += '.' + i
        res += '(' + macro[1:].replace('Device', '') + ')\n'
        
        # add PARENT macro
        saveType = child.getAttribute('SaveType')
        type = child.getAttribute('Type') 
        if (saveType == 'SM' or saveType == 'HM') and not type == 'object':
            par_macro = get_oam_macro_by_uri(uri + '.' + name)
            res += '#define PARENT_' + par_macro + ' '
            space_len = 150 - len(par_macro)
            for i in range(1, space_len):
                res += ' '
               
            par_macro = ''
            num = 0
            arr = uri.split('.')        
            if arr[0] == 'Device':
                del arr[0]
            if arr[0] == 'Services':
                del arr[0]
            for i in arr:
                if i == '0':
                    par_macro += '[(' + key[num] +')-1]'
                    num += 1
                else:
                    par_macro += '.' + i
            res += '(' + par_macro[1:].replace('Device', '') + ')\n'

        if child.getAttribute('Type') == 'object':
            if name == '0':
                res += build_oam_macro(project, child, uri + '.' + name)
                return res
            else:
                res += build_oam_macro(project, child, uri + '.' + name)
        
    return res

def build_oam_cm_update_req_handle(node, uri):
    oam_macro = get_oam_macro_by_uri(uri + '.' + node.getAttribute('Name'))
    sname = node.getAttribute('Sname')
    if len(sname) == 0:
        sname = get_macro_by_uri(uri + '.' + node.getAttribute('Name'))
    funStr = '    sprintf(value, "%d", ' + oam_macro + ')\n'
    funStr += '    ftl_setValue(' + sname + ', value);\n'
    return funStr


def macroExpand(name, depth=0):
    v='i,j,k'
    w='x,y,z'
    while w != '' and '(' + w + ')' not in name:
        w = w[:-2]
    if w != '':
        name = name.replace('(' + w + ')', '(' + v[:max(len(w), depth)] + ')')
    elif depth > 0:
        name += '(' + v[:max(len(w), depth)] + ')'
    return name

def getNumberEntryNodeOamMacro(node, uri, name):
    for child in node.childNodes:
        childName = child.getAttribute('Name')
        if childName.find(name) >= 0 and childName.find('NumberOf') > 0:
            return get_oam_macro_by_uri(uri + '.' + childName)
    return ''


def getMaxNumNodeOamMacro(node, uri, name):
    for child in node.childNodes:
        childName = child.getAttribute('Name')
        if childName.find(name) >= 0 and childName.find('Max') >= 0:
            return get_oam_macro_by_uri(uri + '.' + childName)
    return ''

# ftl_oam_dm_init(void)
def build_oam_dm_init(project, node, uri, depth = 0):
    inner_loop = chr(ord('i') + depth)
    res = ''
    support=''
    if project == 'lte':
        support='F'
    if project == 'tds':
        support='T'
    for child in node.childNodes:

        if not child.getAttribute('Support') == support and not child.getAttribute('Support') == 'C':
            continue
        paraType = child.getAttribute('Type').lower()
        name = child.getAttribute('Name')

        #!TODO
        # we need support n Dimension when n >= 2
        # we need change the function to read the multi object by instance id
        # because instance id may be '2,3,4' when NumberOfEntry is 3
        if paraType == 'object':
            # to build multi object
            if child.childNodes[0].getAttribute('Name') == '0':
                maxNum = macroExpand(getMaxNumNodeOamMacro(node, uri, name), depth)
                if len(maxNum) == 0:
                    maxNum = '32'
                EntryNumMacro = macroExpand(getNumberEntryNodeOamMacro(node, uri, name), depth)
                res += '    if((' + EntryNumMacro + ' > 0) &&\n       (' + EntryNumMacro + ' <= ' +\
                    maxNum + '))\n'
                res += '    {\n'
                res += '        for(' + inner_loop + ' = 1; ' + inner_loop + ' <= ' + EntryNumMacro + '; ' + inner_loop + '++)\n'
                res += '        {\n'
                res += build_oam_dm_init(project, child, uri + '.' + name, depth + 1)

                res += '        }\n    }\n\n'
                continue

            # Only need template node, ignore instance node of multi object
            if name == '0':
                res += build_oam_dm_init(project, child, uri + '.' + name, depth)
                break
            res += build_oam_dm_init(project, child, uri + '.' + name, depth)
            # parse next child node
            continue

        path = uri + '.' + name
        # For Parameter Node
        # for multi Dimension 
        #!TODO need to add multi Dimension support when n >= 2
        # Now the soultion is only support n = 1
        if path.find('.0.') >= 0:
            res += '            sprintf(sname, ' + get_macro_by_uri(path)
            for v in "ijk"[0:depth]:
                res += ', ' + v
            res += ');\n'
            if paraType.find('int') >= 0 or paraType.find('boolean') >= 0:
                res += '            ftl_getNodeValue(sname, buf);\n'
                res += '            ' + macroExpand(get_oam_macro_by_uri(path), depth) + ' = atoi(buf);\n'
            else:
                res += '            ftl_getNodeValue(sname, ' + macroExpand(get_oam_macro_by_uri(path), depth) + ');\n'

            continue

        # for parameter thar not in Multi Object
        if paraType.find('int') >= 0 or paraType.find('boolean') >= 0:
            res += '    ftl_getNodeValue(' + macroExpand(get_macro_by_uri(uri + '.' + name), depth) + ', ' + \
                'buf);\n'
            res += '    ' + get_oam_macro_by_uri(uri + '.' + name) + ' = atoi(buf);\n\n'
        else:
            res += '    ftl_getNodeValue(' + macroExpand(get_macro_by_uri(uri + '.' + name), depth) + ', ' + \
                get_oam_macro_by_uri(uri + '.' + name) + ');\n\n'


    return res 
 
def get_oam_macro_by_uri1(uri):
    num = 0
    res = ''
    arr = uri.split('.')
    for i in arr:
        if i == '0':
            num += 1
    macro = '_'.join(arr)
    res = macro.replace('_0', '').replace('Device_Services_', '')
    v = 'i,j,k'
    if num > 0:
        res += '(' + v[0:num*2-1] + ')'
    return res 

# ftl_oam_sm_init(void)
def build_oam_sm_init(project, node, uri, pre_macro_name = 'FAPService', depth = 0):
    inner_loop = chr(ord('i') + depth)
    res=''
    support=''
    if project == 'lte':
        support='F'
    if project == 'tds':
        support='T'
    for child in node.childNodes:
        if not child.getAttribute('Support') == support and not child.getAttribute('Support') == 'C':
            continue
            
        name = child.getAttribute('Name')
        paraType = child.getAttribute('Type')
        saveType = child.getAttribute('SaveType')
        macro_name = get_oam_macro_by_uri1(uri + '.' + name)
        child_is_have_sm = find_sm(project, child)

        if paraType == 'object':
            # For multi object '0' node is used as template to generator struct code,
            # other instance list like '1', '2' ... , will be ignored
            # to build multi object
            sm = find_sm(project, child.childNodes[0])
            if (child.childNodes[0].getAttribute('Name') == '0'): 
                if not sm == 1:
                    continue

                #if not pre_macro_name == 'NULL':
                tmp_pre_macro_name = '(void *)&' + pre_macro_name
                    
                maxNum = macroExpand(getMaxNumNodeOamMacro(node, uri, name), depth)
                if len(maxNum) == 0:
                    maxNum = '32'
                    
                res += '    for (' + inner_loop + ' = 1; ' + inner_loop + ' <= ' + maxNum + '; ' + inner_loop + '++)\n'
                res += '    {\n'
                res += '        ' + macro_name + '(' + inner_loop + ').__par = ' + tmp_pre_macro_name + ';\n'
                res += build_oam_sm_init(project, child, uri + '.' + name, macro_name + '(' + inner_loop + ')', depth + 1)
                res += '    }\n'
                continue
            
            
            if name == '0':
                res += build_oam_sm_init(project, child, uri + '.' + name, pre_macro_name, depth)
                break
                
            if child_is_have_sm == 1:
                res += '    ' + macro_name
                #if pre_macro_name == 'NULL':
                #    res += '.__par = NULL;\n'
                #else:
                res += '.__par = (void *)&' + pre_macro_name + ";\n"
            else:
                macro_name = pre_macro_name
            
            res += build_oam_sm_init(project, child, uri + '.' + name, macro_name, depth)
            if child_is_have_sm == 1:
                res += '\n'       

    return res

def get_zero_num_by_uri(uri):
    arr = uri.split('.')
    index = ['i', 'j', 'k', 'l', 'm', 'n']
    
    num = 0
    for i in range(0, len(arr) - 1):
        if arr[i] == '0':
            num += 1
    
    return num
    
# build_oam_sm_update_req_handle(void)
def build_oam_sm_update_req_handle(project, node, uri, depth = 0, indent_depth=1):
    inner_loop = chr(ord('i') + depth)
    res=''
    support=''
    if project == 'lte':
        support='F'
    if project == 'tds':
        support='T'
    for child in node.childNodes:
        if not child.getAttribute('Support') == support and not child.getAttribute('Support') == 'C':
            continue
        name = child.getAttribute('Name')
        paraType = child.getAttribute('Type')
        saveType = child.getAttribute('SaveType')
        macro_name = get_oam_macro_by_uri1(uri + '.' + name)
        path = uri + '.' + name

        if paraType == 'object':
            # For multi object '0' node is used as template to generator struct code,
            # other instance list like '1', '2' ... , will be ignored
            # to build multi object 
            if (child.childNodes[0].getAttribute('Name') == '0'): 
                is_have_sm = find_sm(project, child.childNodes[0])
                if not is_have_sm == 1:
                    continue
                
                if saveType == 'SM' or saveType == 'HM':
                    maxNum = macroExpand(getMaxNumNodeOamMacro(node, uri, name))
                    if len(maxNum) == 0:
                        maxNum = '32'
                    EntryNumMacro = macroExpand(getNumberEntryNodeOamMacro(node, uri, name))
                    EntrySnameMacro = macroExpand(getNumberEntryNodeSnameMacro(node, uri, name))

                    # Before copy data to CML, we need check the instance number
                    # if the instance number is more , we need do ftl_addObj
                    # else do ftl_delObj
                    #
                    if EntrySnameMacro.find('_i_') >= 0:
                        res += add_indent('    ', indent_depth)
                        res += '    sprintf(sname,' + EntrySnameMacro + ', i);\n'
                        res += add_indent('    ', indent_depth)
                        res += '    ftl_getNodeValue(sname, buf);\n'
                    else:
                        res += add_indent('    ', indent_depth)
                        res += '    ftl_getNodeValue(' + EntrySnameMacro + ', buf);\n'
                    res += add_indent('    ', indent_depth)
                    res += '    if (' + EntryNumMacro + ' > atoi(buf))\n'
                    res += add_indent('    ', indent_depth)
                    res += '    {\n'
                    res += add_indent('    ', indent_depth)
                    res += '        for (j = atoi(buf)+1; j <= ' + EntryNumMacro + '; j++)\n'
                    res += add_indent('    ', indent_depth)
                    res += '        {\n'
                
                    if EntrySnameMacro.find('_i_') >= 0:
                        res += add_indent('    ', indent_depth)
                        res += '            sprintf(sname, ' + macroExpand(get_macro_by_uri(path)) + '_Table, i);\n'
                        res += add_indent('    ', indent_depth)
                        res += '            ftl_addObj(sname , j);\n'
                    else:
                        res += add_indent('    ', indent_depth)
                        res += '            ftl_addObj(' + macroExpand(get_macro_by_uri(path)) + '_Table, j);\n'
                    res += add_indent('    ', indent_depth)
                    res += '        }\n'
                    res += add_indent('    ', indent_depth)
                    res += '    }\n'
                
                    res += add_indent('    ', indent_depth)
                    res += '    else if (' + EntryNumMacro + ' < atoi(buf))\n'
                    res += add_indent('    ', indent_depth)
                    res += '    {\n'
                    res += add_indent('    ', indent_depth)
                    res += '        for (j = ' + EntryNumMacro + '+1; j <= atoi(buf); j++)\n'
                    res += add_indent('    ', indent_depth)
                    res += '        {\n'
                    if EntrySnameMacro.find('_i_') >= 0:
                        res += add_indent('    ', indent_depth)
                        res += '            sprintf(sname, ' + macroExpand(get_macro_by_uri(path)) + '_Table, i);\n'
                        res += add_indent('    ', indent_depth)
                        res += '            ftl_delObj(sname , j);\n'
                    else:
                        res += add_indent('    ', indent_depth)
                        res += '            ftl_delObj(' + macroExpand(get_macro_by_uri(path)) + '_Table, j);\n'
                    res += add_indent('    ', indent_depth)
                    res += '        }\n'
                    res += add_indent('    ', indent_depth)
                    res += '    }\n\n'
                
                # Set NumberOfEntries                
                maxNum = macroExpand(getMaxNumNodeOamMacro(node, uri, name), depth)
                if len(maxNum) == 0:
                    maxNum = '32'
                
                res += add_indent('    ', indent_depth)
                res += '    for (' + inner_loop + ' = 1; ' + inner_loop + ' <= ' + maxNum + '; ' + inner_loop + '++)\n'
                res += add_indent('    ', indent_depth)
                res += '    {\n'
                res += add_indent('    ', indent_depth)
                res += '        if (' + macro_name + '(' + inner_loop + ').__dirty == 1' + ")\n"
                res += add_indent('    ', indent_depth)
                res += '        {\n'
                res += build_oam_sm_update_req_handle(project, child, uri + '.' + name, depth + 1, indent_depth + 1)
                res += add_indent('    ', indent_depth)
                res += '        }\n'
                res += add_indent('    ', indent_depth)
                res += '    }\n\n'
                continue
                
            child_is_have_sm = find_sm(project, child)    
            if name == '0':
                res += build_oam_sm_update_req_handle(project, child, uri + '.' + name, depth, indent_depth)
                indent_depth -= 1
                break

            
            if child_is_have_sm == 1:
                res += add_indent('    ', indent_depth)
                res += '    if (' + macro_name + '.__dirty == 1 )\n'
                res += add_indent('    ', indent_depth)
                res += '    {\n'
                indent_depth += 1
            
            res += build_oam_sm_update_req_handle(project, child, uri + '.' + name, depth,indent_depth)
            if child_is_have_sm == 1:
                res += add_indent('    ', indent_depth)
                res += '}\n\n'
                indent_depth -= 1
        else:
            if saveType == 'SM' or saveType == 'HM':
                if path.find('.0.') >= 0:
                    res += add_indent('    ', indent_depth)
                    res += '        sprintf(sname, ' + get_macro_by_uri(path)
                    zero_num = get_zero_num_by_uri(path)
                    for v in "ijk"[0:zero_num]:
                        res += ', ' + v
                    res += ');\n'
                    
                    if paraType.find('int') >= 0 or paraType.find('unsigned') >= 0 or paraType.find('boolean') >= 0:
                        res += add_indent('    ', indent_depth)
                        res += '        sprintf(value, "%d", ' + macroExpand(get_oam_macro_by_uri(path)) + ');\n'
                        res += add_indent('    ', indent_depth)
                        res += '        ftl_setValue(sname, value);\n'
                    else:
                        res += add_indent('    ', indent_depth)
                        res += '        ftl_setValue(sname, ' + macroExpand(get_oam_macro_by_uri(path)) + ');\n'
                    if saveType == 'HM':
                        res += add_indent('    ', indent_depth)
                        res += '        commit_flag = 1;\n'
                else:
                    # for parameter thar not in Multi Object
                    if paraType.find('int') >= 0 or paraType.find('unsigned') >= 0 or paraType.find('boolean') >= 0:
                        res += add_indent('    ', indent_depth)
                        res += '    sprintf(value, "%d", ' + macroExpand(get_oam_macro_by_uri(path)) + ');\n'
                        res += add_indent('    ', indent_depth)
                        res += '    ftl_setValue(' + macroExpand(get_macro_by_uri(path)) + ', value);\n'
                    else:
                        res += add_indent('    ', indent_depth)
                        res += '    ftl_setValue(' + macroExpand(get_macro_by_uri(path)) + ', ' + macroExpand(get_oam_macro_by_uri(path)) + ');\n'
                    if saveType == 'HM':
                        res += add_indent('    ', indent_depth)
                        res += '    commit_flag = 1;\n'
    return res
    
def getNumberEntryNodeSnameMacro(node, uri, name):
    for child in node.childNodes:
        childName = child.getAttribute('Name')
        if childName.find(name) >= 0 and childName.find('NumberOf') >= 0:
            return get_macro_by_uri(uri + '.' + childName)
    return ''


# ftl_oam_cm_update_req_handler(void)
def build_oam_cm_update_req_handle(project, node, uri, depth = 0):
    inner_loop = chr(ord('i') + depth)
    res = ''
    support=''
    if project == 'lte':
        support='F'
    if project == 'tds':
        support='T'
    for child in node.childNodes:
        if not child.getAttribute('Support') == support and not child.getAttribute('Support') == 'C':
            continue
        paraType = child.getAttribute('Type').lower()
        name = child.getAttribute('Name')
        path = uri + '.' + name
        # skip NumberOfEntry Node here
        # we will set this value when read the table
        if name.find('NumberOf') >= 0:
            continue

        #!TODO
        # we need support n Dimension when n >= 2
        # we need change the function to read the multi object by instance id
        # because instance id may be '2,3,4' when NumberOfEntry is 3
        if paraType == 'object':
            # to build multi object
            # Before copy data to CML, we need check the instance number
                # if the instance number is more , we need do ftl_addObj
                # else do ftl_delObj
                #
                
            if child.childNodes[0].getAttribute('Name') == '0':
                maxNum = macroExpand(getMaxNumNodeOamMacro(node, uri, name))
                if len(maxNum) == 0:
                    maxNum = '32'
                EntryNumMacro = macroExpand(getNumberEntryNodeOamMacro(node, uri, name))
                EntrySnameMacro = macroExpand(getNumberEntryNodeSnameMacro(node, uri, name))

                # Before copy data to CML, we need check the instance number
                # if the instance number is more , we need do ftl_addObj
                # else do ftl_delObj
                #
                if EntrySnameMacro.find('_i_') >= 0:
                    res += '    sprintf(sname,' + EntrySnameMacro + ', i);\n'
                    res += '    ftl_getNodeValue(sname, buf);\n'
                else:
                    res += '    ftl_getNodeValue(' + EntrySnameMacro + ', buf);\n'
                res += '    if(' + EntryNumMacro + ' > atoi(buf))\n'
                res += '    {\n'
                res += '        for(j = atoi(buf)+1; j <= ' + EntryNumMacro + '; j++)\n'
                res += '        {\n'
                if EntrySnameMacro.find('_i_') >= 0:
                    res += '            sprintf(sname, ' + macroExpand(get_macro_by_uri(path)) + '_Table, i);\n'
                    res += '            ftl_addObj(sname , j);\n'
                else:
                    res += '            ftl_addObj(' + macroExpand(get_macro_by_uri(path)) + '_Table, j);\n'
                res += '        }\n'
                res += '    }\n'

                res += '    else if(' + EntryNumMacro + ' < atoi(buf))\n'
                res += '    {\n'
                res += '        for(j = ' + EntryNumMacro + '+1; j <= atoi(buf); j++)\n'
                res += '        {\n'
                if EntrySnameMacro.find('_i_') >= 0:
                    res += '            sprintf(sname, ' + macroExpand(get_macro_by_uri(path)) + '_Table, i);\n'
                    res += '            ftl_delObj(sname , j);\n'
                else:
                    res += '            ftl_delObj(' + macroExpand(get_macro_by_uri(path)) + '_Table, j);\n'
                res += '        }\n'
                res += '    }\n'
                # Set NumberOfEntries
                res += '    sprintf(value, "%d", ' + EntryNumMacro + ');\n'
                if EntrySnameMacro.find('_i_') >= 0:
                    res += '    sprintf(sname,' + EntrySnameMacro + ', i);\n'
                    res += '    ftl_setValue(sname, value);\n'
                else:
                    res += '    ftl_setValue(' + EntrySnameMacro + ', value);\n'

                #!TODO we need copy data by instance id , like '2,3,4' we should support

                # Copy Data
                res += '    if(' + EntryNumMacro + ' > 0)\n'
                res += '    {\n'
                res += '        for(' + inner_loop + ' = 1; ' + inner_loop + ' <= ' + EntryNumMacro + '; ' + inner_loop + '++)\n'
                res += '        {\n'
                res += build_oam_cm_update_req_handle(project, child, uri + '.' + name, depth+1)

                res += '        }\n    }\n\n'
                continue

            # Only need template node, ignore instance node of multi object
            if name == '0':
                res += build_oam_cm_update_req_handle(project, child, uri + '.' + name, depth)
                break
            res += build_oam_cm_update_req_handle(project, child, uri + '.' + name, depth)
            # parse next child node
            continue

        path = uri + '.' + name
        # For Parameter Node
        # for multi Dimension 
        #!TODO need to add multi Dimension support when n >= 2
        # Now the soultion is only support n = 1
        if path.find('.0.') >= 0:
            res += '            sprintf(sname, ' + get_macro_by_uri(path)
            for v in "ijk"[0:depth]:
                res += ', ' + v
            res += ');\n'
            if paraType.find('int') >= 0 or paraType.find('boolean') >= 0:
                res += '            sprintf(value, "%d", ' + macroExpand(get_oam_macro_by_uri(path)) + ');\n'
                res += '            ftl_setValue(sname, value);\n'
            else:
                res += '            ftl_setValue(sname, ' + macroExpand(get_oam_macro_by_uri(path)) + ');\n'
            continue

        # for parameter thar not in Multi Object
        if paraType.find('int') >= 0 or paraType.find('boolean') >= 0:
            res += '    sprintf(value, "%d", ' + macroExpand(get_oam_macro_by_uri(path)) + ');\n'
            res += '    ftl_setValue(' + macroExpand(get_macro_by_uri(path)) + ', value);\n\n'
            
        else:
            res += '    ftl_setValue(' + macroExpand(get_macro_by_uri(path)) + ', ' + macroExpand(get_oam_macro_by_uri(path)) + ');\n\n'

    return res


# parameter: oam is a dictonary to store the genration code for OAM
# oam['getFun'] : 

def build_oam_files(node, uri, oam):
    uri += '.' + node.getAttribute('Name')
    for child in node.childNodes:
        if child.getAttribute('Type') == 'object':
            build_oam_files(child, uri, oam)
        else:

            if not child.getAttribute('Support') == 'F':
                continue
            print(build_oam_get_fun(project, child, uri))


def print_ori_xml_file(c):
    f = open('ori.xml', 'w')
    f.write(c.write())
    f.close

# For Unit Test
if __name__=='__main__':
    from excel_parse import excel_reader
    from cml import Cml
    print('Test....')
    r = excel_reader('SC-05-11-0209_LTE-Small-Cell-Data-Model_v3.18_20140114.xls')
    #print(r.read_version())
    c = Cml()
    #c.add_child('', {'Name':'Device', 'Type':'Object'})
    r.parse_sheet_by_line('Device(TR-181-2)', c.add_child)
    r.parse_multi_object('Multi Object default', c)
    #res = build_oam_para_struct(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService', '    ', 0)
    #print(res)
    #res = ''
    #res = build_oam_struct_typedef(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService' )
    #print(res)

    #res = ''
    #res = build_oam_macro(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService')
    #print(res)
    res = ''
    res = build_oam_get_fun_head(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService')
    print(res)
    res = ''
    res = build_oam_convert_table(c.getElementsByUri('Device.Services.FAPService.1'), 'Device.Services.FAPService')
    print(res)
    #print(c.write())
    #c.build_sname_header()
    #build_webfiles(c.getElementsByUri('Device'), 'Device')
    #save_file()
    #print_femto_default_xml(c)
    #print_ori_xml_file(c)
