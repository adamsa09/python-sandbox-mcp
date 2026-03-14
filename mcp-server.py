from mcp.server.fastmcp import FastMCP
import subprocess, os, tempfile, sys
from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP("Execute Code", json_response=True, transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False))

VENV_INTERPRETER = sys.executable

@mcp.tool()
def execute(code: str):
    """
    Execute a python snippet in an isolated temporary directory. Use this to solve mathematical equations, physics equations, compute any numerical results, or generate plots. Returns stdout, stderr, and exit code.
    """

    with tempfile.TemporaryDirectory() as workingdir:
        script_path = os.path.join(workingdir, "run.py")
        with open(script_path, "w") as f:
            f.write(code)

        result = subprocess.run(
                [VENV_INTERPRETER, script_path],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=workingdir,
        )
    
    return {
        "ok": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode,
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
