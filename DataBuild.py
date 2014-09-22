if __name__=='__main__':
    from excel_parse import excel_reader
    import os
    import sys, getopt
    opts, args = getopt.getopt(sys.argv[1:], 'f:')
    for op, value in opts:
        if op == '-f':
            filename = value

    reader = excel_reader(filename)
    arr = []
    arr = reader.parse_product_info('Product Information')
    i = 0
    for i in range(0, len(arr)):
        build_cmd = 'python CreateRAWXml.py -f ' + filename + ' -p ' + arr[i]
        os.system(build_cmd)
