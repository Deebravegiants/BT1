# [M] gemini-bridge vulnerable to arbitrary local file read via consult_gemini_with_files inline mode

## Summary
Severity: Medium
Advisory: GHSA-c5px-58j2-7fqp
CVE: CVE-2026-54785
CWE: CWE-200, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-c5px-58j2-7fqp
Type: github-advisory

## Affected
- PyPI: `gemini-bridge` — affected >=1.0.0 <1.3.1

## Details
### Summary
`consult_gemini_with_files` in **inline mode** read any file path supplied in
the `files` argument without confining it to the working `directory`, then
forwarded the contents to the Gemini CLI. Because the caller also controls
`query`, the file contents are echoed back through the Gemini round-trip
(and sent to Google), making this an arbitrary local file read.

### Impact
An MCP client — or an LLM that has been prompt-injected into calling the tool —
can read **any file the server process can access** (SSH keys, cloud
credentials, `.env`, source) and have it disclosed via the tool response.
No code execution by itself.

### Affected component
- Tool: `consult_gemini_with_files(query, directory, files, …)`, `mode="inline"`
- Sink: `_read_file_for_inline` via `_prepare_inline_payload` in `src/mcp_server.py`
- The `at_command` mode already confined paths; inline mode did not.

### Root cause
`_resolve_path` returned an out-of-root path while only nullifying the *display*
name, and `_prepare_inline_payload` read the file regardless. Absolute paths,
`..` traversal, and symlink escapes were all accepted.

### Patch
Fixed in **1.3.1**. `_resolve_path` now resolves symlinks and confines via
`Path.relative_to(root)`; inline mode skips any entry that resolves outside the
working directory (the same guard `at_command` already enforced).

### Workarounds
Upgrade to 1.3.1. Before upgrading, avoid `mode="inline"` with untrusted
`files` input, or run the server with a restricted-permission user.

### Credit
Reported privately by Zhihao Zhang (WPI).

## References
- https://github.com/eLyiN/gemini-bridge/security/advisories/GHSA-c5px-58j2-7fqp
- https://github.com/eLyiN/gemini-bridge/pull/9
- https://github.com/eLyiN/gemini-bridge/commit/8f3b85afd02b692c4bc974b5176e12fb277ea801
- https://github.com/eLyiN/gemini-bridge
- https://github.com/eLyiN/gemini-bridge/releases/tag/v1.3.1
