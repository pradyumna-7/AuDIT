import json
from jinja2 import Environment, FileSystemLoader
import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Set up GPT API Key (store securely as an environment variable)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Set in GitHub secrets or .env file

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
                model="gpt-4o",  # Use the specific GPT model
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
            if not route.get("docstring"):  # If no description exists, call GPT
                route["docstring"] = self.call_gpt(route)

        # Render HTML
        template = self.env.get_template("swagger_template.html")
        html_content = template.render(routes=routes)

        # Write HTML to file
        with open(output_file, "w") as f:
            f.write(html_content)

        print(f"Documentation generated at {output_file}")


if __name__ == "__main__":
    # Load routes
    with open("routes.json", "r") as f:
        routes = json.load(f)

    # Generate documentation
    generator = DocumentationGenerator()
    generator.generate(routes)
