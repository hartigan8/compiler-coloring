import sys
import clang.cindex

def traverse(node):
    if node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
        print(node.displayname, node.kind, node.location)
    for child in node.get_children():
        traverse(child)

def main():
    index = clang.cindex.Index.create()
    tu = index.parse("test.c", args=['-x', 'c'])
    traverse(tu.cursor)

if __name__ == '__main__':
    main()
