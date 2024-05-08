import clang.cindex
import networkx as nx
import matplotlib.pyplot as plt

class Line:
    def __init__(self, decl, number, return_stmt):
        self.decl = decl
        self.refs = []
        self.number = number
        self.return_stmt = return_stmt


class Function:
    def __init__(self, name):
        self.name = name
        self.lines = nx.DiGraph()
        self.alive_values = []
        self.decl_list = []
    
    def print(self):
        for line in self.topological_order:
            if type(line) == clang.cindex.Cursor:
                print(f"line: {line.location.line}, kind: {line.kind}")
            if line.number is not None:
                print("line: %d, decl: %s, refs: %s , return: %s" % (line.number, line.decl, line.refs, line.return_stmt))
            


    def find_line(self,number):
        for line in self.lines:
            if line.number == number:
                return line
        return None
    def reverse(self):
        self.lines = self.lines.reverse(copy=True)
    
    def add_line(self, previous_line, line):
        # Ensure the line is added as a node first
        if line not in self.lines:
            self.lines.add_node(line)

        # If there is a previous line, connect it
        if previous_line is not None:
            self.lines.add_edge(previous_line, line)
        

    @property
    def topological_order(self):
        try:
            return list(nx.topological_sort(self.lines))
        except nx.NetworkXUnfeasible:
            print("Graph has a cycle and cannot be topologically sorted.")
            return []



    
def process_rhs(node, line):
    if node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
        line.refs.append(node.spelling)
    rhs_children = node.get_children()
    for child in rhs_children:
        process_rhs(child, line)

def process_binary_operator(node):
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



def process_var_decl(node, functions, current_func, line):
    if node.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
        fun = functions[current_func]
        line.refs.append(node.displayname)
    children = node.get_children()
    for child in children:
        process_var_decl(child, functions, current_func, line)


def process_compound_assignment(node, functions, current_func, line):
    children = node.get_children()
    for child in children:
        if child.kind == clang.cindex.CursorKind.DECL_REF_EXPR:
            if child.spelling not in line.refs:
                line.refs.append(child.spelling)
        process_compound_assignment(child, functions, current_func, line)


def traverse(node, functions, current_func = "", previous_line = None):
    line = None

    if node.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
        line = process_binary_operator(node)
        if line is not None:
            functions[current_func].add_line(previous_line, line)

    # get first child of the node
    if node.kind == clang.cindex.CursorKind.COMPOUND_ASSIGNMENT_OPERATOR:
        children = node.get_children()
        child = next(children)
        expression = next(children)
        line = Line(child.spelling, node.location.line, False)
        line.refs.append(child.spelling)
        functions[current_func].add_line(previous_line, line)

        process_compound_assignment(expression, functions, current_func, line)

    if(node.kind == clang.cindex.CursorKind.RETURN_STMT):   
        children = node.get_tokens()
        line = Line(node.displayname, node.location.line,True)
        for child in children:
            if child.kind == clang.cindex.TokenKind.IDENTIFIER:
                line.refs.append(child.spelling)    
        functions[current_func].add_line(previous_line, line)
    if node.kind == clang.cindex.CursorKind.DECL_STMT:
        children = node.get_children()
        for child in children:

            if  child.kind == clang.cindex.CursorKind.VAR_DECL:
                line = Line(child.displayname, child.location.line, False)
                functions[current_func].add_line(previous_line, line)

                functions[current_func].decl_list.append(child.displayname)
                process_var_decl(child, functions, current_func, line)
    
    if node.kind == clang.cindex.CursorKind.COMPOUND_STMT:
        children = node.get_children()
        for child in children:
            line = traverse(child, functions, current_func, previous_line)
            functions[current_func].add_line(previous_line, line)
            previous_line = line
    # 1. if statement
    # 2. inside of if
    # 3. else statement -> compound statement, else if -> if statement
    if node.kind == clang.cindex.CursorKind.IF_STMT:
        end_line = Line(None, None, False)
        children = node.get_children()
        inside_of_if = next(children)
        if_line = Line(None, inside_of_if.location.line, False)
        process_rhs(inside_of_if, if_line)
        functions[current_func].add_line(previous_line, if_line)
        functions[current_func].add_line(if_line, end_line)
        for child in children:
            line = traverse(child, functions, current_func, if_line)
            functions[current_func].add_line(if_line, line)
            functions[current_func].add_line(line, end_line)

        line = end_line

    return line
    
    
def process_function(node, functions):
    if(node.kind == clang.cindex.CursorKind.FUNCTION_DECL):
        functions[node.spelling] = Function(node.displayname)
        current_func = node.spelling
        previous_line = None
        cmp_stm = next(node.get_children())
        for child in cmp_stm.get_children():
            previous_line = traverse(child, functions, current_func, previous_line)
    for child in node.get_children():
        process_function(child, functions)

def liveliness_analysis(functions):
    vals = list(functions.values())
    
    for func in vals:
        nx.draw(func.lines, cmap=plt.cm.jet)
        plt.show()
        alive_values = []
        func.reverse()
        func.print()
        i = 0
        for line in func.topological_order:
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
    for func in functions.values():
        plt.figure()  # create a new figure for each function
        G = nx.Graph()
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

    plt.show()  # show all figures at once
    return plt



def main(file_path):
    functions = {}
    index = clang.cindex.Index.create()
    tu = index.parse(file_path, args=['-x', 'c'])

    if tu.diagnostics:
        for dig in tu.diagnostics:
            print(dig)
        raise Exception(tu.diagnostics)

    process_function(tu.cursor, functions)
    liveliness_analysis(functions)
    plt = to_graph(functions)
    return plt

if __name__ == '__main__':
    main("test.c")
