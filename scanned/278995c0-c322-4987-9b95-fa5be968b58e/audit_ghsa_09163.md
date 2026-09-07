# [H] PraisonAI vulnerable to unauthenticated arbitrary file read via MCP workflow.show, workflow.validate, deploy.validate

## Summary
Severity: High
Advisory: GHSA-9cr9-25q5-8prj
CVE: CVE-2026-47394
CWE: CWE-200, CWE-22, CWE-862
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-9cr9-25q5-8prj
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.6.40

## Details
## Summary

The fix for GHSA-9mqq-jqxf-grvw / CVE-2026-44336 is incomplete. The original advisory description named four vulnerable handlers in `mcp_server/adapters/cli_tools.py`:

> "registers four file-handling tools by default, `praisonai.rules.create`, `praisonai.rules.show`, `praisonai.rules.delete`, **and `praisonai.workflow.show`**. Each accepts a path or filename string from MCP `tools/call` arguments… **with no containment check**."

Commit `68cc9427` ("fix(security): harden MCP rules path handling…") added a `_resolve_rule_path()` helper and applied it to `rules.create`, `rules.show`, and `rules.delete`. `workflow.show` was left unchanged. Two adjacent handlers in the same file have the same pattern, `workflow.validate` and `deploy.validate`. Neither was mentioned in the original advisory. Both remain unchanged.

The original advisory also identified the dispatcher (`server.py:281-298`) as a root cause. It accepts unvalidated `**kwargs` from `params["arguments"]` with no enforcement against the tool's declared `input_schema`. That code is unchanged in HEAD as of commit `42221210`.

**Result**: A single unauthenticated MCP `tools/call` to `praisonai.workflow.show` returns the contents of any file the host user can read: `/etc/passwd`, `~/.ssh/id_rsa`, `~/.aws/credentials`, or any project `.env`.

## Affected functionality

`src/praisonai/praisonai/mcp_server/adapters/cli_tools.py`:

| Lines | Tool | Bug |
|-------|------|-----|
| 63-73 | `praisonai.workflow.show` | Returns the full contents of any file the host user can read |
| 42-61 | `praisonai.workflow.validate` | Reads any path; YAML parser error messages leak file existence + content fragments |
| 415-432 | `praisonai.deploy.validate` | Same pattern as `workflow.validate`. The `config_path="deploy.yaml"` default does not constrain the input. |

`src/praisonai/praisonai/mcp_server/server.py:281-298`, `_handle_tools_call`:

```python
async def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    ...
    tool = self._tool_registry.get(tool_name)
    ...
    if asyncio.iscoroutinefunction(tool.handler):
        result = await tool.handler(**arguments)        # ← no schema enforcement
    else:
        result = tool.handler(**arguments)
```

Any JSON arguments the MCP client sends become a `**kwargs` call to the handler. The original advisory pointed at this code path as the root cause. The May 3 patch did not change it.

## Default deployment is exposed

`src/praisonai/praisonai/mcp_server/transports/http_stream.py:38-91`:

- `host` defaults to `127.0.0.1`, which is still reachable from any local process or container neighbour on loopback.
- `api_key` defaults to `None`. The auth check at `http_stream.py:192-198` is gated on `if self.api_key:`, so it is skipped when no key is configured. There is no env var or config switch that turns auth on by default.
- The same handlers are also reachable on the stdio transport, which is the exploitation model the original advisory was written around (Claude Desktop, Cursor, Continue.dev, Claude Code).

## Other file-read sinks reachable via the same dispatcher

These were not named in the original advisory. They confirm the bug is dispatcher-wide and not limited to `cli_tools.py`:

- `mcp_server/adapters/capabilities.py:19-28`, `praisonai.audio.transcribe(file_path)`. Opens any host file and ships it to OpenAI Whisper.
- `mcp_server/adapters/extended_capabilities.py:47-62`, `praisonai.files.create(file_path)`. Uploads any host file to OpenAI Files. A follow-up call to `praisonai.files.content(file_id)` (`extended_capabilities.py:103-113`) returns the bytes.
- `mcp_server/adapters/extended_capabilities.py:243-258`, `praisonai.ocr_extract(image_path)`. Opens any image, returns OCR text.

The three handlers in `cli_tools.py` are the most direct primitives, since they echo the file content back without an OpenAI round-trip.

## Proof of Concept

### Layout
```
PraisonAI/
└── poc/
    ├── start_mcp_server.sh         ← starts the real MCP server
    ├── run_mcp_poc_video.sh        ← runs the attack with curl
    ├── venv/                       
    └── output/
        ├── mcp_server_run.log
        ├── mcp_attacker_run.log
        └── synthetic_credentials.txt   (PoC-only fake creds)
```

[start_mcp_server.sh](https://github.com/user-attachments/files/27569524/start_mcp_server.sh)
[run_mcp_poc_video.sh](https://github.com/user-attachments/files/27569525/run_mcp_poc_video.sh)

The server starter runs the real `MCPServer` class with `register_cli_tools()`, same code path `praisonai mcp serve --transport http-stream` uses. No mocks.

### How to reproduce

**Terminal 1, start the server**:
```bash
cd PraisonAI
bash poc/start_mcp_server.sh
```
Boots `MCPServer` on `127.0.0.1:8766/mcp` with no auth, matching the documented default `api_key=None`.

**Terminal 2, run the attack**:
```bash
cd PraisonAI
bash poc/run_mcp_poc_video.sh
```
Six numbered steps. Each one prints the action, runs one `curl`, prints the JSON-RPC response.

**`workflow.validate` leaks `/etc/hosts`:**
```json
{ "result": { "content": [{ "type": "text",
  "text": "YAML error: while scanning for the next token\nfound character '\\t' that cannot start any token\n  in \"/etc/hosts\", line 7, column 10" }] } }
```
The parser error message confirms the file exists and includes a fragment of its content.

**`deploy.validate` leaks `~/.ssh/known_hosts`:**
```json
{ "result": { "content": [{ "type": "text",
  "text": "Error: expected '<document start>', but found '<scalar>'\n  in \"/Users/<victim>/.ssh/known_hosts\", line 1, column 13" }] } }
```

**`workflow.show` exfiltrates a credential file:**
```json
{ "result": { "content": [{ "type": "text",
  "text": "# AWS-style credentials (SYNTHETIC, for PoC only)\n[default]\naws_access_key_id = AKIA-FAKE-EXFIL-KEY-FOR-POC\naws_secret_access_key = synthetic-secret-do-not-actually-exist-12345\n\n# .env-style secrets\nDATABASE_URL=postgres://app:hunter2@db.internal/prod\nSLACK_BOT_TOKEN=xoxb-FAKE-TOKEN-for-poc-only\nOPENAI_API_KEY=sk-FAKE-FOR-POC\n" }] } }
```

The PoC writes its own synthetic credential file so the demonstration does not depend on the reviewer's real secrets. The same call reads `~/.ssh/id_rsa`, `~/.aws/credentials`, or any project `.env` if you point it there.

https://github.com/user-attachments/assets/09511e66-6a52-4fe3-a303-91d1f99cd27a


## Impact

- Confidentiality, High. Any file the praisonai user can read becomes available to the MCP caller. Typical targets are host SSH keys, cloud credentials, API tokens, project `.env` files, `~/.netrc`, `~/.docker/config.json`, browser cookie databases, and the system password file.
- No authentication required. The default is `api_key=None` (`http_stream.py:91`). The auth check at `http_stream.py:192-198` is wrapped in `if self.api_key:`, so it does not run when no key is configured.
- No operator misconfiguration required. This is the documented default.
- The original advisory's exploitation model still applies. An MCP-connected LLM whose context contains attacker-controlled web pages, documents, or emails can be steered into issuing the same `tools/call` and returning the response. No operator click is needed beyond "summarise this page".

The original advisory was Critical because the write primitive (rules.create) chained to RCE through `.pth` injection. This finding is the read half of the same shape. Read alone is enough to take SSH keys, cloud credentials, and tokens, which is usually how the rest of the host gets compromised through credential reuse.

## Suggested fix

There are two ways to fix this. Doing both is fine. The dispatcher fix is preferred because it closes the same class of bug for every handler that takes a path-shaped argument, including the OpenAI-backed ones called out earlier.

### 1. Enforce `tool.input_schema` in the dispatcher

`mcp_server/server.py:281-298`. The schemas are already built reflectively from each handler's signature in `registry.py:320-376`. Validate `arguments` against the registered schema before calling `tool.handler(**arguments)` and reject anything that does not match. This covers `workflow.show`, `workflow.validate`, `deploy.validate`, `audio.transcribe`, `files.create`, `ocr_extract`, and any handler added later.

### 2. Per-handler containment

This is the same shape as the existing `_resolve_rule_path()` helper added in commit `68cc9427`:

```python
# cli_tools.py
def _resolve_workflow_path(file_path: str) -> Path:
    """Restrict workflow file_path to an allowed root."""
    if not isinstance(file_path, str) or not file_path:
        raise ValueError("file_path must be a non-empty string")
    if "\x00" in file_path or file_path.startswith("~"):
        raise ValueError(f"invalid file_path: {file_path!r}")
    workflows_root = Path(os.path.expanduser("~/.praison/workflows")).resolve()
    workflows_root.mkdir(parents=True, exist_ok=True)
    candidate = (workflows_root / file_path).resolve()
    try:
        candidate.relative_to(workflows_root)
    except ValueError:
        raise ValueError(f"invalid file_path: {file_path!r}")
    return candidate
```

Apply the same helper to:

- `workflow_show(file_path)` and `workflow_validate(file_path)`. Restrict to a workflow root.
- `deploy_validate(config_path)`. Restrict to a deploy-config root or an explicit allowlist.
- The `default="deploy.yaml"` fallback resolves into the user's current working directory. Containment is what fixes the bug, but removing that default also makes prompt-injection chains harder.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-9cr9-25q5-8prj
- https://github.com/MervinPraison/PraisonAI
