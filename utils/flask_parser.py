import ast
import os

class FlaskRouteParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_routes(self):
        with open(self.file_path, "r") as file:
            tree = ast.parse(file.read())

        routes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and getattr(decorator.func, "id", None) == "route":
                        route_path = decorator.args[0].s if decorator.args else None
                        http_methods = (
                            [arg.s for arg in decorator.keywords[0].value.elts]
                            if decorator.keywords else ["GET"]
                        )
                        routes.append({
                            "path": route_path,
                            "methods": http_methods,
                            "function_name": node.name,
                            "docstring": ast.get_docstring(node),
                        })
        return routes
