import sys
symbolTableStack = []
functionReturnAddressStack = []
debug = 0
def usage():
    print 'Usage: <python> <runTime.py> <program.am>'
    exit(-1)
def read_program():
    debug = 1;
    program = []
    i=0
    try:
        if (len(sys.argv) < 2 ):
            usage()
        with open(sys.argv[1]) as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                program.append(line)
                i = i + 1
    except IOError as e:
        print "I/O error -", e.strerror
        exit(-1)
    return program

def consol_log(data):
    if debug:
        print data

def look_up(key):
    function_scope = False
    if key == 'TRUE' or key =='FALSE':
        return key
    try:
        key = int(key)
        return key
    except:
        for i in range(len(symbolTableStack)-1, -1, -1):
            if type(symbolTableStack[i]) == dict:
                if key in symbolTableStack[i]:
                    value = symbolTableStack[i][key]
                    try:
                        value =  int(value)
                        return value
                    except:
                        return value;
                if symbolTableStack[i]['type'] == 'FUNCTION':
                    function_scope = True
                    break;
        if key in symbolTableStack[0]:
            try:
                value = symbolTableStack[0][key]
                value = int (value)
                return value
            except:
                 return value
        report_error(key)

def update_symbol_table(key, val):
    function_scope = False
    try:
        for i in range(len(symbolTableStack) - 1, -1, -1):
            if type(symbolTableStack[i]) == dict:
                if key in symbolTableStack[i]:
                    symbolTableStack[i][key] = val
                    return True
                if symbolTableStack[i]['type'] == 'FUNCTION':
                    function_scope = True
                    break;

        if function_scope and key in symbolTableStack[0]:
                symbolTableStack[0][key] = val
                return True
    except:
        print 'Exception in look up function'
        exit(-1)
    return False
def get_end_of_block():
    search = None
    if symbolTableStack[-1]['type'] == 'IF':
        search = 'IEND'
    elif symbolTableStack[-1]['type'] == 'WHILE':
        search = 'WEND'
    else:
        report_error(None)
    return search

def report_error(var):
    if var == None:
        print "ERROR: syntax error in the program"
    else:
        print "ERROR: variable", var, 'is not defined'
    exit(-1)

def compare_values(val1, val2, flag):
    try:
        val1 = int (val1)
        val2 = int (val2)
        if flag == 'NQ':
            if val1 > val2:
                return 1
            elif val1 < val2:
                return -1
            else:
                return 0
        else:
            if val1 >= val2:
                return 1
            elif val1 <= val2:
                return -1
            else:
                return 2
    except:
        if ((val1 == 'TRUE' or val1 == 'FALSE') and (val2 == 'TRUE' or val2 == 'FALSE')):
            if (val1 == val2):
                return 0
            else:
                return 2
        else:
            print "ERROR: Type mismatch while comparing values"
            exit(-1)
        # write code to handle booleans
def get_comparision_result(v1, v2, flag):
    v1 = look_up(v1)
    v2 = look_up(v2)
    result = compare_values(v1, v2, flag)
    return result

def add_to_symbol_table(key, val):
    try:
        for i in range(len(symbolTableStack) - 1, -1, -1):
            if type(symbolTableStack[i]) == dict:
                symbolTableStack[i][key] = val
                return True
    except:
        print 'Exception in look up function'
        exit(-1)
    return False

def check_types(val1, val2):
    if ((val1 == 'TRUE' or val1 == 'FALSE') and (val2 == 'TRUE' or val2 == 'FALSE')):
        return
    try:
        val1 = int (val1)
        val2 = int (val2)

    except:
        print "ERROR: Type mismatch while performing arithmetic operation"
        exit(-1)

def execute_program(program):

    symbolTableStack.append({}) # global symbol table
    symbolTableStack[0]['type'] = 'GLOBAL'
    line = 0
    noOfLines = len(program)
    fincName = None
    ifExecuted = False
    elseExecuted = False
    formalArgumentsStack = []
    while line < noOfLines:
        contents = program[line].split(' ')
        if (contents[0] == 'FSTR'):
            symbolTableStack[-1][contents[1]] = line+1
            line  = line + 1
            while(line < noOfLines and not program[line].startswith('FEND')):
                line = line + 1

        elif contents[0] == 'MOVE': #when assigning
            if symbolTableStack[-1]['type'] == 'FUNCTION':
                symbolTableStack[-1][contents[1]] = look_up(contents[2])
            else:
                r_value = update_symbol_table(contents[1], look_up(contents[2]))
                if not r_value:
                    symbolTableStack[-1][contents[1]] = look_up(contents[2])
            consol_log(symbolTableStack)


        elif contents[0] == 'FCAL':
           funcName = contents[1]

        elif contents[0] == 'PSTR':
            'Pass'

        elif contents[0] == 'PUSH':
            value = look_up(contents[1])
            formalArgumentsStack.append(value)


        elif contents[0] == 'PEND':

            funcSymbolTable = {}
            funcSymbolTable['type'] = 'FUNCTION'
            symbolTableStack.append(funcSymbolTable)
            functionReturnAddressStack.append(line + 1)

            for i in range(len(formalArgumentsStack)-1, -1, -1):
                symbolTableStack.append(formalArgumentsStack[i])

            if funcName == None:
                report_error(funcName)
            try:
                line = symbolTableStack[0][funcName]
            except:
                report_error(funcName)
            funcName = None
            formalArgumentsStack = []
            line -= 1
            consol_log(symbolTableStack)

        elif contents[0] == 'ISTR' or contents[0] == 'WSTR':
            symTable = {}
            if contents[0] == 'ISTR':
                symTable['type'] = 'IF'
                ifExecuted = False
            else:
                symTable['type'] = 'WHILE'
                symTable['start_loop'] = line  #loop start
            symbolTableStack.append(symTable)
            consol_log(symbolTableStack)


        elif contents[0] == 'CEQL' or contents[0] == 'CLES' or contents[0] == 'CGTR':
            result = get_comparision_result(contents[1], contents[2], 'NQ')
            search = get_end_of_block()
            if (result == 0 and contents[0] == 'CEQL') or (result == 1 and contents[0] == 'CGTR') or (result == -1 and contents[0] == 'CLES'):
                if symbolTableStack[-1]['type'] == 'IF':
                    ifExecuted = True
            else:
                while not program[line].startswith(search):
                    if (search == 'WEND'):
                        symbolTableStack[-1]['exit_loop'] = True
                    line += 1
                line -= 1


        elif contents[0] == 'CNQL' or contents[0] == 'CLSE' or contents[0] == 'CGTE':
            result = get_comparision_result(contents[1], contents[2], 'EQ')
            search = get_end_of_block()
            if (result == 2 and contents[0] == 'CNQL') or (result == 1 and contents[0] == 'CGTE') or (
                    result == -1 and contents[0] == 'CLSE'):
                if symbolTableStack[-1]['type'] == 'IF':
                    ifExecuted = True
            else:
                while not program[line].startswith(search):
                    if (search == 'WEND'):
                        symbolTableStack[-1]['exit_loop'] = True
                    line += 1
                line -= 1

        elif contents[0] == 'IEND':

            symbolTableStack.pop()
            consol_log(symbolTableStack)

        elif contents[0] == 'ESTR':

            if not ifExecuted :
                elseExecuted = True
                elseStack = {}
                elseStack['type'] = 'ELSE'
                symbolTableStack.append(elseStack);
            else:
                line += 1
                contents = program[line].split(' ')
                while not program[line].startswith('EEND'):
                    line += 1
                line -= 1

        elif contents[0] == 'EEND':
            ifExecuted = False
            if elseExecuted:
                symbolTableStack.pop()
            elseExecuted = False
            consol_log(symbolTableStack)

        elif contents[0] == 'WEND':
            if 'exit_loop' not in symbolTableStack[-1]:
                line = symbolTableStack[-1]['start_loop']
            else:
                symbolTableStack.pop()

        elif contents[0] == 'SEND':
            val = None
            try:
                val = int (contents[1])
            except:
                val = look_up(contents[1])
            index = len(symbolTableStack) - 1;
            while (symbolTableStack[index]['type'] != 'FUNCTION'):
                symbolTableStack.pop()
                index -= 1
            if index >=0 and symbolTableStack[index]['type'] == 'FUNCTION':
                line = functionReturnAddressStack[-1]
                functionReturnAddressStack.pop()
                symbolTableStack.pop()
                line = line -1
                symbolTableStack.append(val)
            else:
                print "ERROR: Illegal return statement in the scope"
            consol_log(symbolTableStack)

        elif contents[0] == 'LOAD': # for return value only
            val = symbolTableStack[-1]
            try:
                val = int(val)
            except:
                'Pass'
            #print 'val: ',val
            symbolTableStack.pop()
            add_to_symbol_table(contents[1], val)
            consol_log(symbolTableStack)

        elif contents[0] == 'PRNT':
            val = look_up(contents[1])
            print val

        elif contents[0] == 'SPRNT':
            print contents[1],

        elif contents[0] == 'FEND':
            symbolTableStack.pop()
            line = functionReturnAddressStack[-1]
            functionReturnAddressStack.pop()
            line -= 1
            consol_log(symbolTableStack)
        elif contents[0] == 'STACK':
            add_to_symbol_table(contents[1], [])

        elif contents[0] == 'SPUSH':
            st = look_up(contents[1])
            st.append(int(contents[2]))
            update_symbol_table(contents[1], st)
            consol_log(symbolTableStack)

        elif contents[0] == 'SPOP':
            st = look_up(contents[1])
            rValue = st.pop()
            add_to_symbol_table(contents[2], rValue)
            update_symbol_table(contents[1], st)
            consol_log(symbolTableStack)

        elif contents[0] == 'SEMPTY':
            st = look_up(contents[1])
            if len(st) == 0:
               update_symbol_table(contents[2], 'TRUE')
            else:
                update_symbol_table(contents[2], 'FALSE')

            consol_log(symbolTableStack)

        elif contents[0] == 'MULT':
            n1 = look_up(contents[2])
            n2 = look_up(contents[3])
            check_types(n1, n2)
            v = n1 * n2
            r_value = update_symbol_table(contents[1], v)
            if not r_value:
                symbolTableStack[-1][contents[1]] = v
            consol_log(symbolTableStack)

        elif contents[0] == 'ADD':
            n1 = look_up(contents[2])
            n2 = look_up(contents[3])
            check_types(n1, n2)
            v = n1 + n2
            r_value = update_symbol_table(contents[1], v)
            if not r_value:
                symbolTableStack[-1][contents[1]] = v
            consol_log(symbolTableStack)

        elif contents[0] == 'SUB':
            n1 = look_up(contents[2])
            n2 = look_up(contents[3])
            check_types(n1, n2)
            v = n1 - n2
            r_value = update_symbol_table(contents[1], v)
            if not r_value :
                symbolTableStack[-1][contents[1]] = v
            consol_log(symbolTableStack)

        elif contents[0] == 'DIV':
            n1 = look_up(contents[2])
            n2 = look_up(contents[3])
            check_types(n1, n2)
            v = n1 / n2
            r_value = update_symbol_table(contents[1], v)
            if not r_value:
                symbolTableStack[-1][contents[1]] = v
            consol_log(symbolTableStack)

        line += 1


if __name__ == "__main__":
    program = read_program()
    consol_log(program)
    execute_program(program)
    consol_log(symbolTableStack)
