import sys
import clang.cindex






class Function:
    def __init__(self, name):
        self.name = name
        self.lines = []
    
    def print(self):
        for line in self.lines:
            print("line: %d, decl: %s, refs: %s , return: %s" % (line.number, line.decl, line.refs, line.return_stmt))

    def find_line(self, lines, number):
        for line in lines:
            if line.number == number:
                return line
        return None
    

class Line:
    def __init__(self, decl, number,return_stmt):
        self.decl = decl
        self.refs = []
        self.number = number
        self.return_stmt = return_stmt

    



def traverse(node, functions, current_func = ""):
    if(node.kind == clang.cindex.CursorKind.FUNCTION_DECL):
        functions[node.spelling] = Function(node.displayname)
        current_func = node.spelling
        
    if(node.kind == clang.cindex.CursorKind.RETURN_STMT):
        functions[current_func].lines.append(Line(node.displayname, node.location.line,True))
        
    if  node.kind == clang.cindex.CursorKind.VAR_DECL:
        functions[current_func].lines.append(Line(node.displayname, node.location.line,False))

    if node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
        fun = functions[current_func]
        line = fun.find_line(functions[current_func].lines, node.location.line)
        if line:
            line.refs.append(node.displayname)
    for child in node.get_children():
        traverse(child, functions, current_func)



def main():
    functions = {}
    index = clang.cindex.Index.create()
    tu = index.parse("test.c", args=['-x', 'c'])
    traverse(tu.cursor, functions)
    for func in functions.values():
        func.print()
        print("\n")


if __name__ == '__main__':
    main()
