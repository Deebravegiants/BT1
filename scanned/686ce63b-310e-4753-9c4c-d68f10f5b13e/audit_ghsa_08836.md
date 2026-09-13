# [M] wireshark-mcp vulnerable to arbitrary file write via export_objects when WIRESHARK_MCP_ALLOWED_DIRS is not configured

## Summary
Severity: Medium
Advisory: GHSA-3r68-x3xc-rxpg
CVE: CVE-2026-43901
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-3r68-x3xc-rxpg
Type: github-advisory

## Affected
- PyPI: `wireshark-mcp` — affected >=0

## Details
## Description

### Impact

`wireshark-mcp` exposes a `wireshark_export_objects` MCP tool that accepts an attacker-controlled `dest_dir` parameter and passes it to tshark's `--export-objects` flag with **no mandatory path restriction**.

The path sandbox (`_allowed_dirs`) is `None` by default and only activates when the environment variable `WIRESHARK_MCP_ALLOWED_DIRS` is explicitly set. In a default installation, any directory on the filesystem can be used as the export destination.

**Affected code** (`src/wireshark_mcp/tshark/client.py:531-543`):

```python

output_validation = self._validate_output_path(dest_dir)

# _validate_output_path only enforces the sandbox when _allowed_dirs is set.

# Default: _allowed_dirs = None → no restriction.

os.makedirs(dest_dir, exist_ok=True)   # creates arbitrary directories

cmd = [..., "--export-objects", f"{protocol},{dest_dir}"]

```

### Attack Scenario

An attacker embeds a crafted HTTP response in a pcap file (e.g. `Content-Disposition: filename=authorized_keys`). Via prompt injection in the pcap payload, an AI model using this MCP server is manipulated into calling `wireshark_export_objects` with:

```bash

dest_dir=/home/user/.ssh/

```

`tshark` then extracts and writes the HTTP object to that path, granting the attacker SSH access.

The same technique can target:

- `/etc/cron.d/`

- Writable web roots

- Other sensitive filesystem locations

### Additional Affected Operations

The same missing sandbox affects:

- `merge_pcap_files`

- `editcap_trim`

- `editcap_split`

- `editcap_time_shift`

- `editcap_deduplicate`

- `text2pcap_import`

### Proof of Concept

Confirmed on **wireshark-mcp v1.1.5** with **tshark 4.6.4**.

A crafted pcap’s HTTP object was successfully written to an arbitrary filesystem path when:

```python

_allowed_dirs = None

```

---

## Patches

Not yet patched.

A fix should make the path sandbox **mandatory** for all file-write operations rather than optional:

```python

# Reject all write operations when no sandbox is configured

if not self._allowed_dirs:

    return json.dumps({

        "success": False,

        "error": {

            "type": "SecurityError",

            "message": "Set WIRESHARK_MCP_ALLOWED_DIRS before using file-write operations"

        }

    })

```

---

## Workarounds

Set `WIRESHARK_MCP_ALLOWED_DIRS` to a restricted safe directory before starting the server:

```bash

export WIRESHARK_MCP_ALLOWED_DIRS=/tmp/wireshark_mcp_safe

```

This activates the existing sandbox and blocks writes outside the allowed path.

---

## Resources

- Vulnerable code:

  - `src/wireshark_mcp/tshark/client.py` lines 521–543

  - `src/wireshark_mcp/tshark/client.py` lines 685–839

- CWE-22: Improper Limitation of a Pathname to a Restricted Directory

- CWE-73: External Control of File Name or Path

## References
- https://github.com/bx33661/Wireshark-MCP/security/advisories/GHSA-3r68-x3xc-rxpg
- https://nvd.nist.gov/vuln/detail/CVE-2026-43901
- https://github.com/bx33661/Wireshark-MCP
