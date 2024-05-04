import sys
import clang.cindex

class Line:
    def __init__(self, decl, number):
        self.decl = decl
        self.refs = []
        self.number = number

def find_line(lines, number):
    for line in lines:
        if line.number == number:
            return line
    return None

def traverse(node, lines):
    if(node.kind == clang.cindex.CursorKind.RETURN_STMT):
        print("Return statement found at line: %d" % node.location.line)
        
    if  node.kind == clang.cindex.CursorKind.VAR_DECL:
        lines.append(Line(node.displayname, node.location.line))

    if node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
        line = find_line(lines, node.location.line)
        if line:
            line.refs.append(node.displayname)
    for child in node.get_children():
        traverse(child, lines)



def main():
    lines = []
    index = clang.cindex.Index.create()
    tu = index.parse("test.c", args=['-x', 'c'])
    traverse(tu.cursor, lines)
    for line in lines:
        print("line: %d, decl: %s, refs: %s" % (line.number, line.decl, line.refs))

if __name__ == '__main__':
    main()
