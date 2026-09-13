# [C] DevSpace vulnerable to remote code execution

## Summary
Severity: Critical
Advisory: GHSA-6h8c-gw33-cjm2
CVE: CVE-2020-15391
CWE: CWE-287, CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-6h8c-gw33-cjm2
Type: github-advisory

## Affected
- Go: `github.com/loft-sh/devspace` — affected >=0 <4.14.0

## Details
The UI in DevSpace 4.13.0 allows web sites to execute actions on pods (on behalf of a victim) because of a lack of authentication for the WebSocket protocol. This leads to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15391
- https://github.com/devspace-sh/devspace/issues/1128
- https://github.com/devspace-cloud/devspace/releases/tag/v4.14.0
- https://github.com/devspace-sh/devspace
