# [M] mcp-server-git : Path traversal in git_add allows staging files outside repository boundaries

## Summary
Severity: Medium
Advisory: GHSA-vjqx-cfc4-9h6v
CVE: CVE-2026-27735
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-02-26
Source: https://github.com/advisories/GHSA-vjqx-cfc4-9h6v
Type: github-advisory

## Affected
- PyPI: `mcp-server-git` — affected >=0 <2026.1.14

## Details
In `mcp-server-git` versions prior to 2026.1.14, the `git_add` tool did not validate that file paths provided in the files argument were within the repository boundaries. The tool used GitPython's `repo.index.add(`, which did not enforce working-tree boundary checks for relative paths. As a result, relative paths containing `../` sequences that resolved outside the repository were accepted and staged into the Git index, potentially allowing sensitive files to be exfiltrated via subsequent commit and push operations. The fix in PR #3164 switches to `repo.git.add()`, which delegates to the Git CLI and properly rejects out-of-tree paths. Users are advised to upgrade to 2026.1.14 or newer to remediate this issue.

mcp-server-git thanks https://hackerone.com/0dd-g for reporting and contributing the fix.

## References
- https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-vjqx-cfc4-9h6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-27735
- https://github.com/modelcontextprotocol/servers/pull/3164
- https://github.com/modelcontextprotocol/servers/commit/862e717ff714987bd5577318df09858e14883863
- https://github.com/modelcontextprotocol/servers
