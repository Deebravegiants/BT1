# [H] automagik-genie has a command injection vulnerability

## Summary
Severity: High
Advisory: GHSA-64vr-4gr2-m642
CVE: CVE-2026-30635
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-64vr-4gr2-m642
Type: github-advisory

## Affected
- npm: `automagik-genie` — affected 2.5.27

## Details
Command injection vulnerability in automagik-genie 2.5.27 MCP Server allows attackers to execute arbitrary commands via the view_task (aka view) in the readTranscriptFromCommit function in dist/mcp/server.js when a user reads from an external FORGE_BASE_URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-30635
- https://gist.github.com/spdc-elm/3ddecd10ffa85c5963ab7fe531619875
- https://github.com/automagik-dev/genie
