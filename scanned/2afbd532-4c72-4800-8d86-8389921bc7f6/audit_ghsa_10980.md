# [M] Gokapi vulnerable to DoS in E2E Metadata Parser

## Summary
Severity: Medium
Advisory: GHSA-qwc6-vc2v-2ggj
CVE: CVE-2026-30955
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-qwc6-vc2v-2ggj
Type: github-advisory

## Affected
- Go: `github.com/forceu/gokapi` — affected >=0 <2.2.4

## Details
### Summary

An API endpoint accepts unbounded request bodies without any size limit. An authenticated user can cause an OOM kill and complete service disruption for all users.


### Impact

Any authenticated user can crash the Gokapi server by sending concurrent large payloads.

## References
- https://github.com/Forceu/Gokapi/security/advisories/GHSA-qwc6-vc2v-2ggj
- https://nvd.nist.gov/vuln/detail/CVE-2026-30955
- https://github.com/Forceu/Gokapi
- https://github.com/Forceu/Gokapi/releases/tag/v2.2.4
- https://pkg.go.dev/vuln/GO-2026-4698
