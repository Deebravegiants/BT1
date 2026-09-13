# [H] MCP-Salesforce's arbitrary attribute access leads to disclosure of Salesforce auth token

## Summary
Severity: High
Advisory: GHSA-vf6j-c56p-cq58
CVE: CVE-2026-25650
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-vf6j-c56p-cq58
Type: github-advisory

## Affected
- PyPI: `mcp-salesforce-connector` — affected >=0 <0.1.10

## Details
### Impact
_Disclosure of Salesforce OAuth bearer tokens used by the MCP._

### Patches
_fix applied in 0.1.10_

### Workarounds
_Rotate any Salesforce tokens/credentials used by MCP-Salesforce._

## References
- https://github.com/smn2gnt/MCP-Salesforce/security/advisories/GHSA-vf6j-c56p-cq58
- https://nvd.nist.gov/vuln/detail/CVE-2026-25650
- https://github.com/smn2gnt/MCP-Salesforce/commit/a1e3a5a786f48508d066b6d40b58201ebf9b7fd6
- https://github.com/smn2gnt/MCP-Salesforce
- https://github.com/smn2gnt/MCP-Salesforce/releases/tag/v0.1.10
