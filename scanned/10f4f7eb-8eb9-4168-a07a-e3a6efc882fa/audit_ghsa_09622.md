# [C] excel-mcp-server has a Path Traversal issue

## Summary
Severity: Critical
Advisory: GHSA-j98m-w3xp-9f56
CVE: CVE-2026-40576
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-j98m-w3xp-9f56
Type: github-advisory

## Affected
- PyPI: `excel-mcp-server` — affected >=0 <0.1.8

## Details
## Summary

A path traversal vulnerability exists in [`excel-mcp-server`](https://github.com/haris-musa/excel-mcp-server) versions up to and including `0.1.7`. When running in SSE or Streamable-HTTP transport mode (the documented way to use this server remotely), an unauthenticated attacker on the network can read, write, and overwrite arbitrary files on the host filesystem by supplying crafted `filepath` arguments to any of the 25 exposed MCP tool handlers.

The server is intended to confine file operations to a directory set by the `EXCEL_FILES_PATH` environment variable. The function responsible for enforcing this boundary — `get_excel_path()` — fails to do so due to two independent flaws: it passes absolute paths through without any check, and it joins relative paths without resolving or validating the result. Combined with zero authentication on the default network-facing transport and a default bind address of `0.0.0.0` (all interfaces), this allows trivial remote exploitation.

---

## Details

| Field | Value |
|-------|-------|
| **Package** | [`excel-mcp-server`](https://pypi.org/project/excel-mcp-server/) (PyPI) |
| **Repository** | https://github.com/haris-musa/excel-mcp-server |
| **Affected versions** | `<= 0.1.7` |
| **Tested version** | `0.1.7` — commit [`de4dc75`](https://github.com/haris-musa/excel-mcp-server/commit/de4dc75f6ba629ccd2e097f5963235846be622e6) |
| **CWE** | [CWE-22](https://cwe.mitre.org/data/definitions/22.html) — Improper Limitation of a Pathname to a Restricted Directory |
| **CVSS 3.1** | **8.2 High** — `AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H` |
| **Transports affected** | `sse`, `streamable-http` (network-facing) |
| **Authentication required** | **None** |

---

## Vulnerable Code

The root cause is in `src/excel_mcp/server.py`, lines 75–94:

```python
def get_excel_path(filename: str) -> str:
    """Get full path to Excel file."""

    # FLAW 1 — absolute paths bypass the sandbox entirely
    if os.path.isabs(filename):
        return filename                     # line 86: returned as-is

    # In SSE/HTTP mode, EXCEL_FILES_PATH is set
    if EXCEL_FILES_PATH is None:
        raise ValueError(...)

    # FLAW 2 — relative paths joined without boundary validation
    return os.path.join(EXCEL_FILES_PATH, filename)   # line 94: "../" escapes
```

### Why this is exploitable

**Flaw 1 — Absolute path bypass (line 86):**
If the attacker passes `filepath="/etc/shadow"` or `filepath="/home/user/secrets.xlsx"`, the function returns it unchanged. The sandbox directory `EXCEL_FILES_PATH` is never consulted.

**Flaw 2 — Relative traversal (line 94):**
`os.path.join("/srv/sandbox", "../../etc/passwd")` produces `"/srv/sandbox/../../etc/passwd"`, which resolves to `"/etc/passwd"`. No `os.path.realpath()` or `os.path.commonpath()` check is performed, so `../` sequences escape the sandbox.

### Contributing factors that increase severity

1. **Default bind address is `0.0.0.0`** (all interfaces) — `server.py` line 70:
   ```python
   host=os.environ.get("FASTMCP_HOST", "0.0.0.0"),
   ```
   A user who follows the README and runs `uvx excel-mcp-server streamable-http` without explicitly setting `FASTMCP_HOST` exposes the server to their entire LAN.

2. **Zero authentication** — FastMCP's SSE and Streamable-HTTP transports ship with no authentication. The server adds none. Any TCP client that reaches port 8017 can call any tool.

3. **All 25 tool handlers are affected** — every `@mcp.tool()` decorated function calls `get_excel_path(filepath)` as its first action. This is not an isolated endpoint; it is the entire API surface.

4. **Arbitrary directory creation** — `src/excel_mcp/workbook.py` line 24 runs `path.parent.mkdir(parents=True, exist_ok=True)` before saving, meaning the attacker can create directory trees at any writable location.

---

## Proof of Concept

### Video demonstration

[![asciicast](https://asciinema.org/a/2HVA3uKvVeFahIXY.svg)](https://asciinema.org/a/2HVA3uKvVeFahIXY)

**asciinema recording:** https://asciinema.org/a/2HVA3uKvVeFahIXY

I have also attached the full PoC shell script (`record-poc.sh`) and the Python exploit script (`exploit_test.py`) to a Google Drive for the maintainer to review and reproduce independently:

**Google Drive (PoC scripts):**  Shared privately via email

Contents:
- `record-poc.sh` — automated PoC recording script (bash)
- `exploit_test.py` — Python exploit that tests all 7 primitives against a running server

### Setup

```bash
# install
pip install excel-mcp-server mcp httpx

# start server with a sandbox directory
mkdir -p /tmp/sandbox
EXCEL_FILES_PATH=/tmp/sandbox FASTMCP_HOST=127.0.0.1 FASTMCP_PORT=8017 \
    excel-mcp-server streamable-http
```

### Exploit script

The following Python script connects to the server with zero credentials and demonstrates all exploitation primitives:

{REMOVING CAUSE FOR SAFETY CONCERNS}

### Results

All 7 test cases passed against a live server instance:

```
CONFIRMED: 7  |  FAILED: 0

[CONFIRMED] AUTH: Connected with ZERO authentication. 25 tools exposed.
[CONFIRMED] P1-WRITE-ABS: file exists=True size=4783B (outside sandbox)
[CONFIRMED] P2-WRITE-TRAVERSAL: escaped sandbox via ../ exists=True
[CONFIRMED] P3-MKDIR: attacker directory tree created=True
[CONFIRMED] P4-READ: exfiltrated SSN=True name=True
[CONFIRMED] P5-OVERWRITE: victim data replaced=True
[CONFIRMED] P6-STAT: server attempted to open /etc/hostname (format error confirms file access)
```

### Filesystem evidence (independently verified after exploit)

**Files created outside the sandbox:**
```
$ ls -la /tmp/cve-hunt/outside_sandbox/
-rw-rw-r-- 1 hitarth hitarth 4783 Apr 10 17:36 P1_absolute_write.xlsx
-rw-rw-r-- 1 hitarth hitarth 4783 Apr 10 17:36 P2_traversal_write.xlsx
```

**Attacker-created directory tree:**
```
$ find /tmp/cve-hunt/attacker_dir
/tmp/cve-hunt/attacker_dir
/tmp/cve-hunt/attacker_dir/deep
/tmp/cve-hunt/attacker_dir/deep/nested
/tmp/cve-hunt/attacker_dir/deep/nested/x.xlsx
```

**Victim file after overwrite (original SSN destroyed):**
```
  ('SSN', 'Name')
  ('ATTACKER-CONTROLLED', 'PWNED')     # was: ('123-45-6789', 'Alice Johnson')
  ('987-65-4321', 'Bob Smith')
```

---

## Impact

An unauthenticated network attacker can:

| What | How | Severity |
|------|-----|----------|
| **Read any `.xlsx` file** on the host | Supply absolute path to `read_data_from_excel` | Confidentiality loss — cross-tenant data theft of financial data, HR records, reports |
| **Write `.xlsx` files anywhere** on the filesystem | Supply absolute path or `../` traversal to `create_workbook` or `write_data_to_excel` | Integrity loss — destroy or corrupt any writable `.xlsx`, plant malicious files |
| **Create arbitrary directories** anywhere writable | `create_workbook` triggers `mkdir(parents=True)` on attacker-controlled path | Precursor to privilege escalation or DoS |
| **Overwrite existing business files** with attacker content | `write_data_to_excel` with absolute path to target | Silent data corruption — audit reports, salary sheets, financial models |
| **Fill disk** via repeated writes | Loop `create_workbook` with unique filenames | Denial of service — crash services dependent on free disk |
| **Plant macro-enabled templates** (`.xltm`) at known shared paths | `create_workbook` at path like `/home/user/Templates/report.xltm` | Client-side RCE chain when downstream user opens the template in Excel |

### Who is affected

Anyone running `excel-mcp-server` in SSE or Streamable-HTTP mode on a reachable network — which is the documented and recommended deployment for remote use. The project README explicitly states:
- *"Works both locally and as a remote service"*
- *"Streamable HTTP Transport (Recommended for remote connections)"*

The server has **3,655+ GitHub stars** and is published on **PyPI** with active downloads.

---

## Suggested Fix

Replace `get_excel_path()` with a version that enforces the sandbox boundary:

```python
import os

def get_excel_path(filename: str) -> str:
    if EXCEL_FILES_PATH is None:
        # stdio mode: local caller is trusted
        if not os.path.isabs(filename):
            raise ValueError("must be absolute path in stdio mode")
        return filename

    # Remote mode (SSE / streamable-http): enforce sandbox
    if os.path.isabs(filename):
        raise ValueError("absolute paths are not permitted in remote mode")
    if "\x00" in filename:
        raise ValueError("NUL byte in filename")

    base = os.path.realpath(EXCEL_FILES_PATH)
    candidate = os.path.realpath(os.path.join(base, filename))

    if not candidate.startswith(base + os.sep) and candidate != base:
        raise ValueError(f"path escapes EXCEL_FILES_PATH: {filename}")

    return candidate
```

## References

- [CWE-22: Improper Limitation of a Pathname to a Restricted Directory](https://cwe.mitre.org/data/definitions/22.html)
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## References
- https://github.com/haris-musa/excel-mcp-server/security/advisories/GHSA-j98m-w3xp-9f56
- https://nvd.nist.gov/vuln/detail/CVE-2026-40576
- https://github.com/haris-musa/excel-mcp-server/commit/f51340ecd5778952405044b203d3a2d4c8a46833
- https://github.com/haris-musa/excel-mcp-server
