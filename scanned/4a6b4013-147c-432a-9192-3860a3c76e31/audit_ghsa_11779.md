# [H] Gokapi has Stored XSS in SVG Hotlinks

## Summary
Severity: High
Advisory: GHSA-3c22-5j5m-4jq7
CVE: CVE-2026-28683
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-3c22-5j5m-4jq7
Type: github-advisory

## Affected
- Go: `github.com/forceu/gokapi` — affected >=0 <2.2.3

## Details
### Summary
If a malicious authenticated user uploads SVG and creates a hotlink for it, they achieve stored XSS.

### Details
The hotlinking functionality fails to properly handle scripts included in the SVGs, allowing authenticated attackers with the ability to upload and hotlink file to execute arbitrary JS.

*Issue found by [aisafe.io](https://aisafe.io/)*


### Impact
Authenticated attackers with the ability to upload and hotlink files can execute arbitrary JavaScript.

## References
- https://github.com/Forceu/Gokapi/security/advisories/GHSA-3c22-5j5m-4jq7
- https://nvd.nist.gov/vuln/detail/CVE-2026-28683
- https://github.com/Forceu/Gokapi
- https://github.com/Forceu/Gokapi/releases/tag/v2.2.3
