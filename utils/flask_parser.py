import ast
import sys
import json

def parse_flask_routes(file_path):
    """
    Parse Flask routes from a given Python file.
    """
    print(f"Parsing Flask file: {file_path}")  # Debugging line
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read(), filename=file_path)

        routes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                print(f"Checking function: {node.name}")  # Debugging line
                for decorator in node.decorator_list:
                    print(f"Decorator: {ast.dump(decorator)}")  # Debugging line
                    if isinstance(decorator, ast.Call) and (
                        getattr(decorator.func, "id", "") in ["route", "add_url_rule"] or
                        (hasattr(decorator.func, "attr") and decorator.func.attr in ["route", "add_url_rule"])
                    ):
                        methods = []
                        for keyword in decorator.keywords:
                            if keyword.arg == "methods":
                                methods = [elt.s for elt in keyword.value.elts]
                        path = decorator.args[0].s if decorator.args else ""
                        print(f"Found route: {path}, methods: {methods}")  # Debugging line
                        routes.append({
                            "path": path,
                            "methods": methods or ["GET"],
                            "function_name": node.name,
                            "docstring": ast.get_docstring(node),
                        })
        return routes
    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")  # Debugging line
        raise e

if __name__ == "__main__": 
    if len(sys.argv) < 2:
        print("Usage: python flask_parser.py <file1.py> [<file2.py> ...]")
        sys.exit(1)

    routes = []
    for file_path in sys.argv[1:]:
        print(f"Processing file: {file_path}")  # Debugging line
        routes.extend(parse_flask_routes(file_path))

    # Save routes to routes.json
    with open("routes.json", "w") as f:
        json.dump(routes, f, indent=4)

    # Debugging line to verify the saved content
    print("Routes saved to routes.json:")
    with open("routes.json", "r") as f:
        print(f.read())  # Print the content of the saved routes

    print("Flask routes extracted and saved to routes.json.")
