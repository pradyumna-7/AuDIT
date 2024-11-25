const esprima = require('esprima');
const fs = require('fs');

class NodeJsRouteParser {
    constructor(filePath) {
        this.filePath = filePath;
    }

    parseRoutes() {
        const code = fs.readFileSync(this.filePath, 'utf-8');
        const ast = esprima.parseScript(code);

        const routes = [];
        esprima.traverse(ast, {
            enter(node) {
                if (
                    node.type === 'CallExpression' &&
                    node.callee.object &&
                    node.callee.object.name === 'app'
                ) {
                    const method = node.callee.property.name;
                    const path = node.arguments[0].value;
                    routes.push({
                        method: method.toUpperCase(),
                        path: path,
                    });
                }
            },
        });
        return routes;
    }
}

module.exports = NodeJsRouteParser;
