import json
import subprocess
from jinja2 import Environment, FileSystemLoader
import openai
import os
import sys

from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

class DocumentationGenerator:
    def __init__(self, template_dir="templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def call_gpt(self, route):
        """
        Call the GPT API to generate descriptions or enhance route details.
        """
        prompt = f"""
        Here is a route for an API:
        - Method: {route['methods']}
        - Path: {route['path']}
        - Function: {route['function_name']}
        - Current Description: {route.get('docstring', 'None')}

        Generate a detailed description for this route, including its purpose and an example usage.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-0613",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for generating API documentation."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Error with GPT API: {e}")
            return "Description could not be generated."

    def generate(self, routes, output_file="docs/index.html"):
        """
        Generate documentation by enhancing route descriptions with GPT and rendering HTML.
        """
        for route in routes:
            if not route.get("docstring"):
                route["docstring"] = self.call_gpt(route)

        # Render HTML
        template = self.env.get_template("template.html")  # Corrected path
        html_content = template.render(routes=routes)

        # Write HTML to file
        with open(output_file, "w") as f:
            f.write(html_content)

        print(f"Documentation generated at {output_file}")


def run_parsers(flask_files, node_files):
    """
    Run Flask and Node.js parsers on specified files.
    """
    routes = []

    if flask_files:
        # Run Flask parser
        subprocess.run(["python", "utils/flask_parser.py"] + flask_files, check=True)

    if node_files:
        # Run Node.js parser
        subprocess.run(["node", "nodejs_parser.js"] + node_files, check=True)

    # Load parsed routes from routes.json if it exists
    if os.path.exists("routes.json"):
        with open("routes.json", "r") as f:
            routes = json.load(f)

    return routes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_docs.py <flask_file1.py> ... [--node <node_file1.js> ...]")
        sys.exit(1)

    flask_files = []
    node_files = []

    # Separate Flask and Node.js files based on `--node` delimiter
    if '--node' in sys.argv:
        split_index = sys.argv.index('--node')
        flask_files = sys.argv[1:split_index]
        node_files = sys.argv[split_index + 1:]
    else:
        flask_files = sys.argv[1:]

    if not flask_files and not node_files:
        print("No files provided. Specify at least one Flask or Node.js file.")
        sys.exit(1)

    # Run parsers and generate docs
    routes = run_parsers(flask_files, node_files)
    generator = DocumentationGenerator()
    generator.generate(routes)
