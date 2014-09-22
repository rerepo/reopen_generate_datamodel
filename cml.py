import xml.dom.minidom
from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parse
import xml.etree.ElementTree

import re
import string
import codecs
class Cml:
    #import xml.dom.minidom
    #from xml.dom.minidom import getDOMImplementation
    
    def  __init__(self):
        self.doc = getDOMImplementation().createDocument(None, "SERCOMM_CML", None)
        self.root = self.doc.documentElement
       
        return

    def load_file(self, filename):
        #string = open(filename).read().replace('\n', '')
        string = codecs.open(filename, "r", "utf-8").read().replace('\n','')
        self.doc = xml.dom.minidom.parseString(string)
        #self.doc = parse(filename)
        self.root = self.doc.documentElement
        #self.root = xml.etree.ElementTree.parse(filename)

    def add_info(self, info):
        element = self.doc.createElement('Element')
        element.setAttribute('Name', 'info')
        element.setAttribute('version', info['version'])
        element.setAttribute('filename', info['filename'])
        self.root.appendChild(element)

    def value_check(node, value):
        pass

    def add_object_child(self, para):
        # remove the last '.'
        if para['Name'][-1] == '.':
            para['Name'] = para['Name'][0:-1]
    
        arr = para['Name'].split('.')
        
        # Check if this object need to be set as " Normal Object"
        if arr[-1] == '{i}':
            if str(para['Comment']).find('normal object') >= 0:
                arr[-1] = '1'
            else:
                arr[-1] = '0'
        '''
        if arr[-1] == '{i}' :
            if para['Writeable'] == '1':
                arr[-1] = '0'
            else:
                arr[-1] = '1'
        '''

        if len(arr) > 3 and '.'.join(arr[0:-1]).find('{i}') >= 0:

            for i in range(1, len(arr) - 1):
                
                if arr[i] == "{i}":
                     
                    # try 0
                    arr[i] = '0'
                     
                    if self.getElementsByUri('.'.join(arr[0:i+1])) != None:
                        continue
                    else:
                        arr[i] = '1'
                        if self.getElementsByUri('.'.join(arr[0:i+1])) != None:
                            continue
        # 'Device.IP.0'
        # get 'Device'
         
        parent = self.getElementsByUri('.'.join(arr[0:-2]))
        
        if arr[-1] == '0' or arr[-1] == '1':
            element = self.doc.createElement('Element')
            para['Name'] = arr[-2]
            for key in para:
                element.setAttribute(key, para[key])
                parent.appendChild(element)

        # get 'Device.IP.'
        parent = self.getElementsByUri('.'.join(arr[0:-1]))
        element = self.doc.createElement('Element')

        para['Name'] = arr[-1]
        for key in para:
            element.setAttribute(key, para[key])
            parent.appendChild(element)
         
        return '.'.join(arr)




    def add_child(self, uri, para):
        # uri is the URI of parent
        #print(uri + '  ' + para['Name'])

        # If input parameter is object, para['Name'] will be the full path
        # and we will ignore the uri value
        # the return the real URI
    
        if para['Type'] == 'object':
            if para['Name'].find('{i}') >= 0:
                return self.add_object_child(para)
            else:
                # remove the last '.'
                if para['Name'][-1] == '.':
                    para['Name'] = para['Name'][0:-1]
                
                arr = para['Name'].split('.')
                para['Name'] = arr[-1]
                element = self.doc.createElement('Element')
                for key in para:
                    element.setAttribute(key, para[key])
            
                parent = self.getElementsByUri('.'.join(arr[0:-1]))
                 
                if parent == None:
                    parent = self.root
            
                parent.appendChild(element)
                return '.'.join(arr)


        tmp = uri + '.' + para['Name']
        #if type(self.getElementsByUri(tmp)) != None:
            #return 
        element = self.doc.createElement('Element')
        
        for key in para:
            #if len(para[key]) != 0:
                #element.setAttribute(key, para[key])
            element.setAttribute(key, para[key])


        '''
        if para['Type'] != 'object':
            element.appendChild(self.doc.createTextNode(''))
        '''
        if(len(uri) == 0):
            parent = self.root
        else:
            parent = self.getElementsByUri(uri)

        if parent == None:
            #print(uri + '  ' + para['Name'])
            return uri
        parent.appendChild(element)
        
        return uri

    def add_instance(self, uri, id):
        # uri: 'Device.IP"
        #print(uri+'0')
        object_template = self.getElementsByUri(uri+'0')
        if object_template is None:
            object_template = self.getElementsByUri(uri + '1')
        if object_template is None:
            print(uri)
            
        instance = object_template.cloneNode(1)
        instance.setAttribute('Name', str(id))
        parent=self.getElementsByUri(uri[0:-1])
        parent.appendChild(instance)

    def getElementsByUri(self, uri):
        node = self.root
        if len(uri) == 0:
            return self.root
        name = uri.split('.')
        deep = 0
        max_id = len(name) - 1
        flag = 0
        for item in name:
            # bug here
            flag = 0
            for child in node.childNodes:
                
                if child.getAttribute('Name') == item:
                    node = child
                    flag = 1
                    break
            if flag == 0:
                return 
        return node

    def set_para(self, uri, para):
        element = self.getElementsByUri(uri)
        for key in para:
            element.setAttribute(key, para[key])

    def set_value(self, uri, value):
        dic = {}
        dic['Value'] = value
        self.set_para(uri, dic)

    def get_attribute(self, uri, key):
        node = self.getElementsByUri(uri)
        return node.getAttribute(key)
    '''
    def getSnameByUri(self, uri):
        if uri in snameTable.keys():
            return snameTable[uri]
        else:
            arr = uri.split('.')



     #
     # sname_def_dm.h 
     # generator Macro for sname
     # now all sname is full name 
     #
    def h_sname_header(self, node, uri=''):
        index = ['i', 'j', 'k', 'l']

        for child in node.childNodes:
            #uri += ('.' + child.getAttribute('Name'))
            #arr = uri.split('.')
            arr = (uri + '.' + child.getAttribute('Name')).split('.')
            if arr[-1] == '0':
                sname = '.'.join(arr[0:-1]).replace('.0.', '.%d.')
            else:
                sname = '.'.join(arr).replace('.0.', '.%d.')
            # replace '.0' with '.%d'
            p = 0
            for i in range(0, len(arr) - 1):
                if arr[i] == '0':
                    arr[i] = index[p]
                    p += 1
            if arr[1] == 'Services':
                i = 2
            else:
                i = 1

            # Type: object
            # 'Device.IP' -> ignore
            # 'Device.IP.0' -> Deive_IP_Table'
            if child.getAttribute('Type') is 'object':

                if child.getAttribute('Name') != '0':
                    self.h_sname_header(child, uri + '.' + child.getAttribute('Name'))
                    continue
                if arr[-1] == '0':
                    del arr[-1]
                macro = '_'.join(arr[i:]).replace('FAPService_1', 'FAPService').replace('FAP_1', 'FAP')

                print("#define CM_SNAME_"+macro+"_Table ", end='')
                blank = 72 - len(macro) -18 
                if blank > 0:
                    for k in range(1,blank):
                        print(' ', end='')
                print("    \"" + sname + '.\"')

                self.h_sname_header(child, uri + '.' + child.getAttribute('Name'))
            else:

                macro = '_'.join(arr[i:])
                # ignore '1' in FAPService node
                macro = macro.replace('FAPService_1', 'FAPService')
                # ignore '1' in FAP node
                macro = macro.replace('FAP_1', 'FAP')

                ouput = "#define CM_SNAME_"+macro
                blank = 78 - len(macro) -18 
                if blank > 0:
                    for k in range(1,blank):
                        ouput += ' '
                output += "    \"" + sname + '\"'
            return output

    def gen_sname_header(self):
        # begin from the childnode of root.
        # root node will just have only one childnode
        self.h_sname_header(self.getElementsByUri('Device'), 'Device')
    '''
    def write(self):
        return self.doc.toprettyxml(indent="", newl="\n", encoding="utf-8")
        

# Use for Unit Test
if __name__=='__main__':
    pass
