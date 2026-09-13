# [H] FastMCP updated to MCP 1.23+ due to CVE-2025-66416

## Summary
Severity: High
Advisory: GHSA-rcfx-77hg-w2wv
Ecosystem: PyPI
Published: 2025-12-26
Source: https://github.com/advisories/GHSA-rcfx-77hg-w2wv
Type: github-advisory

## Affected
- PyPI: `fastmcp` — affected >=0 <2.14.0

## Details
There was a recent CVE report on MCP: https://nvd.nist.gov/vuln/detail/CVE-2025-66416. 

FastMCP does not use any of the affected components of the MCP SDK directly. However, FastMCP versions prior to 2.14.0 did allow MCP SDK versions <1.23 that were vulnerable to CVE-2025-66416. Users should upgrade to FastMCP 2.14.0 or later.

## References
- https://github.com/jlowin/fastmcp/security/advisories/GHSA-rcfx-77hg-w2wv
- https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-9h52-p55h-vw2f
- https://nvd.nist.gov/vuln/detail/CVE-2025-66416
- https://github.com/jlowin/fastmcp
