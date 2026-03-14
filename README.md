# Python Sandbox MCP for LibreChat

## Goal
Give LibreChat the ability to execute Python code, especially in the context of physics/math/engineering problem solving, without paying for the official LibreChat Code Interpreter API

## Architecture
LibreChat LLM  
`    v    `  
MCP Toolcall  
`    v    `  
Routed via HTTP to `mcp-server.py`, where [mcp](https://pypi.org/project/mcp/#overview) serves the `execute` tool over HTTP via [uvicorn](https://uvicorn.dev/)  
`    v    `  
Python code run in a sandbox (temporary directory created with [tempfile](https://docs.python.org/3/library/tempfile.html))  
`    v    `  
Returned to LLM: `{"ok": bool, "stdout": string, "stderr": string, "exit_code": int}`

## Initial LibreChat config
> [!NOTE]
> Assuming LibreChat `librechat.yaml` is set up. [For help on LibreChat configuration](https://www.librechat.ai/docs/configuration/librechat_yaml)  
`librechat.yaml`
1. Whitelist `host.docker.internal` under mcpSettings  
```
mcpSettings:
  allowedDomains:
    - 'host.docker.internal' 
```  
2. Add the MCP server
```
mcpServers:
    python_sandbox:
      type: streamable-http 
      url: http://host.docker.internal:8000/mcp
      title: "Python Sandbox"
      timeout: 150000
```  
3. Restart LibreChat  
`docker compose down && docker compose up -d # In LibreChat directory`  


## Setup
1. Clone the repo & install dependencies  
```
git clone https://github.com/adamsa09/librechat-code-exec-mcp
cd librechat-code-exec-mcp
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt # python > 3.10 required
```

2. Run the MCP server 
`.venv/bin/python mcp-server.py`

Thats it. The MCP should be available in LibreChat. I recommend building an [agent](https://www.librechat.ai/docs/features/agents) with access to the MCP and adding the following system prompt as a base. It ensures that the model identifies the aspects of the problem and how to attack it:
```
You are a math-based problem solving assistant.

When solving any problem involving calculation, equations, or numerical values:
1. List all given values with units.
2. State the formula you will use.
3. Before calling python_execute, show the code you are about to run in a Python code block.
4. Call python_execute to compute the result. NEVER do arithmetic mentally.
5. Always print results with units and variable names.

Available libraries: numpy, sympy, scipy, matplotlib, pint, uncertainties.
- Use sympy for algebraic/symbolic solving and exact results.
- Use numpy for numerical computation.
- Use pint for unit tracking and conversion.
- Use uncertainties for error propagation in lab problems.
- Use scipy for integrals, ODEs, or advanced physics.
- Use matplotlib only if a graph is explicitly requested.
```

## Compatible models
Using the MCP with weaker models may not work due to unreliable tool calling.

## Adding python modules
Just use pip, and add the model into the system prompt if using an agent so the LLM knows it has access to it.
