import clang.cindex
import networkx as nx
import matplotlib.pyplot as plt


class Function:
    def __init__(self, name):
        self.name = name
        self.lines = []
        self.alive_values = []
        self.decl_list = []
    
    def print(self):
        for line in self.lines:
            print("line: %d, decl: %s, refs: %s , return: %s" % (line.number, line.decl, line.refs, line.return_stmt))

    def find_line(self,number):
        for line in self.lines:
            if line.number == number:
                return line
        return None
    def reverse(self):
        self.lines.reverse()
    

class Line:
    def __init__(self, decl, number, return_stmt):
        self.decl = decl
        self.refs = []
        self.number = number
        self.return_stmt = return_stmt

    
def process_rhs(node, line):
    if node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
        line.refs.append(node.spelling)
    rhs_children = node.get_children()
    for child in rhs_children:
        process_rhs(child, line)

def process_binary_operator(node, line):
    tokens = node.get_tokens()
    for token in tokens:
        if(token.spelling == "="):
            children = node.get_children()
            rhs = None
            lhs = None
            i = 0
            for child in children:
                if i == 0:
                    lhs = child.spelling
                else:
                    rhs = child
                i = i + 1
            line = Line(lhs, node.location.line, False)
            process_rhs(rhs, line)
            return line


def process_var_decl(node, functions, current_func):
    if node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
        fun = functions[current_func]
        line = fun.find_line(node.location.line)
        if line:
            line.refs.append(node.displayname)
    children = node.get_children()
    for child in children:
        process_var_decl(child, functions, current_func)


def process_compound_assignment(node, functions, current_func, line):
    children = node.get_children()
    for child in children:
        if child.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
            if child.spelling not in line.refs:
                line.refs.append(child.spelling)
        process_compound_assignment(child, functions, current_func, line)
        print(child.location.line)
        print(f"{child.spelling} {child.kind}")


def traverse(node, functions, parent=None, depth = 0, current_func = ""):

    if node.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
        
        line = process_binary_operator(node, None)
        if line:
            functions[current_func].lines.append(line)

    # get first child of the node
    if node.kind == clang.cindex.CursorKind.COMPOUND_ASSIGNMENT_OPERATOR:
        children = node.get_children()
        child = next(children)
        expression = next(children)
        line = Line(child.spelling, node.location.line, False)
        line.refs.append(child.spelling)
        functions[current_func].lines.append(line)
        process_compound_assignment(expression, functions, current_func, line)

    if(node.kind == clang.cindex.CursorKind.FUNCTION_DECL):
        functions[node.spelling] = Function(node.displayname)
        current_func = node.spelling

        

    if(node.kind == clang.cindex.CursorKind.RETURN_STMT):
        functions[current_func].lines.append(Line(node.displayname, node.location.line, True))
    
    
    if  node.kind == clang.cindex.CursorKind.VAR_DECL:
        functions[current_func].lines.append(Line(node.displayname, node.location.line, False))
        functions[current_func].decl_list.append(node.displayname)
        process_var_decl(node, functions, current_func)

    for child in node.get_children():
        traverse(child, functions, node, depth, current_func)
    
    


def liveliness_analysis(functions):
    vals = list(functions.values())

    for func in vals:
        alive_values = []
        func.reverse()
        func.print()
        i = 0
        for line in func.lines:
            if len(alive_values) == 0:
                alive_values.append(line.refs)
            else:
                if line.decl in alive_values[i - 1]:
                    prev = alive_values[i - 1].copy()
                    prev.remove(line.decl)
                    for ref in line.refs:
                        if ref not in prev:
                            prev.append(ref)
                    alive_values.append(prev)
                else:
                    prev = alive_values[i - 1].copy()
                    for ref in line.refs:
                        if ref not in prev:
                            prev.append(ref)
                    alive_values.append(prev)
            i = i + 1
        func.alive_values = alive_values
        print(alive_values)
        print("\n")
        

def to_graph(functions):
    G = nx.Graph()
    for func in functions.values():
        decl_list = func.decl_list
        for decl in decl_list:
            G.add_node(decl)
            for alive in func.alive_values:
                if decl in alive:
                    for decl2 in alive:
                        if decl2 != decl:
                            G.add_edge(decl, decl2)
    
    colors = nx.coloring.greedy_color(G)
    node_colors = [colors[n] for n in G.nodes()]

    nx.draw(G, with_labels=True, node_color=node_colors, cmap=plt.cm.jet)
    plt.show()



def main():
    functions = {}
    index = clang.cindex.Index.create()
    tu = index.parse("test.c", args=['-x', 'c'])

    if tu.diagnostics:
        for dig in tu.diagnostics:
            print(dig)
        raise Exception(tu.diagnostics)

    traverse(tu.cursor, functions)
    liveliness_analysis(functions)
    to_graph(functions)


if __name__ == '__main__':
    main()
