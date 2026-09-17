# [H] fast-filesystem-mcp has a Path Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-j893-m93w-jwjw
CVE: CVE-2025-67364
CWE: CWE-24
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-j893-m93w-jwjw
Type: github-advisory

## Affected
- npm: `fast-filesystem-mcp` — affected >=0

## Details
fast-filesystem-mcp version 3.4.0 contains a critical path traversal vulnerability in its file operation tools including fast_read_file. This vulnerability arises from improper path validation that fails to resolve symbolic links to their actual physical paths. The safePath and isPathAllowed functions use path.resolve() which does not handle symlinks, allowing attackers to bypass directory access restrictions by creating symlinks within allowed directories that point to restricted system paths. When these symlinks are accessed through valid path references, the validation checks are circumvented, enabling access to unauthorized files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-67364
- https://github.com/efforthye/fast-filesystem-mcp/issues/10
- https://github.com/efforthye/fast-filesystem-mcp
