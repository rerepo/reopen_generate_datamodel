if __name__=='__main__':
    from excel_parse import excel_reader
    from cml import Cml 

    import sys, getopt
    import os
    import codecs

    toolversion = '1.0.0'
    opts, args = getopt.getopt(sys.argv[1:], 'f:')
    for op, value in opts:
        if op == '-f':
            excel_filename = value

    print('Reading file : ' + excel_filename)
    reader = excel_reader(excel_filename)
    version = reader.read_version() + '.0'

    arr = []
    arr = reader.parse_product_info('Product Information')
    for i in range(0, len(arr)):
        real_name =  arr[i]
        print('Bulid Project : ' + real_name)
        c = Cml()

        info = {}
        info['filename'] = excel_filename
        info['version'] = version
        c.add_info(info)

        reader.parse_sheet_by_line('Device(TR-181-2)', c.add_child, real_name, arr)
        reader.parse_multi_object('Multi Object default', c, real_name)

        res = c.write()
        output = codecs.open(real_name + '_' + 'DataModel_RAW.xml', 'w', "utf-8")
        output.write(res.decode("utf-8"))
        output.close()

    print("Read " + excel_filename + " Successfully!")
