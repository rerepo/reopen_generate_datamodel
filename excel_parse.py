import xlrd
import re

class excel_reader:
    def __init__(self, filename):
        self.book = xlrd.open_workbook(filename)

    def read_version(self):
        table = self.book.sheets()[0]
        nrows = table.nrows
        re_ver = re.compile('^\d\.\d{2}$')
        version = ''
        for i in range(1, nrows - 1):
            if re_ver.match(str(table.col(1)[i].value)) :
                version = table.col(1)[i].value
        return version

    def convert_value(self, ori):
        tmp = ori
        i = len(tmp) - 1
        if len(tmp) > 0 and str(tmp)[-1] == '.':
            return tmp
        if str(tmp)[str(tmp).find('.') + 1:].find('.') > 0:
            return tmp
        if str(tmp).find('.') > 0:
            while i > 0:
                if tmp[i] != '0' and tmp[i] != '.':
                    break
                if tmp[i] == '.':
                    tmp = tmp[0: i]
                    break
                else:
                    tmp = tmp[0: i]
                    i -= 1
        if tmp.find('<Empty>') >= 0:
            tmp = ''
        return tmp

    def parse_default(self, para, name):
        if len(para[name]) != 0:
            if para[name][0] == '\"' and para[name][-1] == '\"':
                para[name] = para[name][1:-2]

            if para[name].find('Empty') > 0:
                para[name] = ''

            if para[name] == "-":
                para[name] = ''
        if para[name].find('Object default') > 0:
            para[name] = ''
        return para

    def read_line(self, table, line_number, content, pname, arr):
        para = {}

        for i in range(0, len(content)):
            para[content[i]] = str(table.row(line_number)[i].value).strip()

        # delete unused parameters
        #del para['Description']
        #del para['EnumData']
        #del para['Comment']

        # Parse Description
        para['Description'] = para['Description'].replace('\r\n', ' newl ')

        # Type
        #para['Type'] = para['Type'].replace(' ', '')

        # Writeable
        if para['Writeable'] == 'W' or para['Writeable'] == 'w':
            para['Writeable'] = '1'
        else:
            para['Writeable'] = '0'

        # sname
        if len(para['Sname']) == 0:
            del para['Sname']

        #parse_default
        if (len(para[pname + '_Default']) != 0) and (para[pname + '_Default'] != para['Default']):
            para = self.parse_default(para, pname + '_Default')
            para['Value'] = self.convert_value(para[pname + '_Default'])
        else:
            para = self.parse_default(para, 'Default')
            para['Value'] = self.convert_value(para['Default'])


        #parse_permission
        if (len(para[pname + '_Permissions']) != 0):
            para['Permissions'] = para[pname + '_Permissions']


        if para['denyActive'] == '1':
            para['denyActive'] = 'True'
        elif para['denyActive'] == '0':
            para['denyActive'] = 'False'
        para['EnumData'] = para['EnumData'].strip().replace('\n', '')
        '''
        tmp = para['Default']
        i = len(tmp) - 1
        if str(tmp).find('.') > 0:
            while i > 0:
                if tmp[i] != '0' and tmp[i] != '.':
                    break
                if tmp[i] == '.':
                    tmp = tmp[0: i]
                    break
                else:
                    tmp = tmp[0: i]
                    i -= 1
        para['Value'] = tmp
        if tmp.find('<Empty>') >= 0:
            tmp = ''
        '''

        if para['Type'] == 'boolean':
            if len(para['Value']) == 0:
                para['Value'] = '0'
            if para['Value'] == 'TRUE' or para['Value'] == 'True' or para['Value'] == '1':
                para['Value'] = '1'
            else: 
                para['Value'] = '0'
        for i in range(0, len(arr)):
            del para[str(arr[i]) + '_Default']
            del para[str(arr[i]) + '_Permissions']

        del para['Default']
        # GUI Page
        para['page'] = para['GUI Page'].replace('\n', '')
        del para['GUI Page']

        del para['Implement']
        del para['Ver']

        if len(para['syntax']) == 0:
            del para['syntax']
        return para

    def parse_sheet_by_line(self, sheetname, fun, pname, arr, uri=''):
        #print('Parse sheet ' + sheetname)
        table = self.book.sheet_by_name(sheetname)

        nrows = table.nrows
        #mapping = table.row_values(0)
        content = table.row_values(0)

        for i in range(1, nrows - 1):
            para = self.read_line(table, i, content, pname, arr)

            if len(para['Support']) == 0:
                continue

            if str(para['Type']) == 'Sheet Name':
                self.parse_sheet_by_line(para['Name'], fun, pname, arr, uri)
                continue
            else:
                uri = fun(uri, para)

    def parse_multi_object(self, sheetname, c, pname):
        table = self.book.sheet_by_name(sheetname)
        i = 2
        while i < table.nrows - 1:
            offset = 3
            find = 0
            end = 0
            index = []
            uri = table.cell(i, 1).value
            if not uri.find('Device') == 0:
                i += 1
                continue
            while offset < table.ncols - 1:
                offset += 1
                if((not table.cell(i, offset).value == '') and (table.cell(i, offset).value == pname)):
                    find = 1
                    break

            if find == 0:
                offset = 3

            arr = []
            j = i + 2
            name = table.cell(j, 1).value
            while not len(str(name)) is 0:
                arr.append(name)
                j += 1
                if j > table.nrows - 1:
                    break
                name = table.cell(j, 1).value
            m = i + 1
            n = 0
            index = table.cell(m, offset).value
            if str(index).find('.') >= 0:
                index=str(index)[0:str(index).find('.')]
            uri = uri.replace('.{i}.', '.')
            while len(index) > 0:
                c.add_instance(uri, int(index))
                for q in range(0, len(arr)):
                    #print(uri + str(index) + '.' + arr[q] + ": " + str(table.cell(m + q + 1, offset + n).value))
                    c.set_value(uri + str(index) + '.' + arr[q], self.convert_value(str(table.cell(m + q + 1, offset + n).value)))
                n += 1
                # avoid out of the range 
                if ((n + offset == table.ncols) or (table.cell(i ,n+offset).value != '')):
                    break
                index = table.cell(m, offset + n).value
                if str(index).find('.') >= 0:
                    index=str(index)[0:str(index).find('.')]
                uri = uri.replace('.{i}.', '.')
            i = j

    def parse_product_info(self, sheetname):
        table = self.book.sheet_by_name(sheetname)
        m = 4
        i = 0
        arr = []
        while m < table.nrows - 1:
            if table.cell(m, 2).value == '':
                break
            arr.append(str(table.cell(m, 2).value) + '_' + str(table.cell(m, 3).value))
            i += 1
            m += 1
        return arr

            
# Use for Unit Test
if __name__=='__main__':
    from cml import Cml
    r = excel_reader('test.xls')
    #print(r.read_version())
    c = Cml()
    #c.add_child('', {'Name':'Device', 'Type':'Object'})
    r.parse_sheet_by_line('Device(TR-181-2)', c.add_child)
    r.parse_multi_object('Multi Object default', c)
    #c.write()
    #c.gen_sname_header()
    c.gen_htm()
