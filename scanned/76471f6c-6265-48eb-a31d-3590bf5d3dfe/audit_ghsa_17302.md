# [M]  mcp-server-git argument injection in git_diff and git_checkout functions allows overwriting local files

## Summary
Severity: Medium
Advisory: GHSA-9xwc-hfwc-8w59
CVE: CVE-2025-68144
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:N/SI:H/SA:L (CVSS_V4)
Published: 2025-12-17
Source: https://github.com/advisories/GHSA-9xwc-hfwc-8w59
Type: github-advisory

## Affected
- PyPI: `mcp-server-git` — affected >=0 <2025.12.18

## Details
In mcp-server-git versions prior to 2025.12.18, the git_diff and git_checkout functions passed user-controlled arguments directly to git CLI commands without sanitization. Flag-like values (e.g., `--output=/path/to/file` for `git_diff`) would be interpreted as command-line options rather than git refs, enabling arbitrary file overwrites. The fix adds validation that rejects arguments starting with - and verifies the argument resolves to a valid git ref via rev_parse before execution. Users are advised to update to 2025.12.18 resolve this issue.

Thank you to https://hackerone.com/yardenporat for reporting.

## References
- https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-9xwc-hfwc-8w59
- https://nvd.nist.gov/vuln/detail/CVE-2025-68144
- https://github.com/modelcontextprotocol/servers
