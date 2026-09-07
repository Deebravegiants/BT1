# [M] Cross site scripting in Cloudreve

## Summary
Severity: Medium
Advisory: GHSA-fg25-gq9g-32mx
CVE: CVE-2022-32167
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-fg25-gq9g-32mx
Type: github-advisory

## Affected
- Go: `github.com/HFO4/cloudreve` — affected >=1.0.0
- Go: `github.com/cloudreve/Cloudreve/v3` — affected >=3.0.0 <3.6.0-beta1

## Details
Cloudreve versions v1.0.0 through v3.5.3 are vulnerable to Stored Cross-Site Scripting (XSS), via the file upload functionality. A low privileged user will be able to share a file with an admin user, which could lead to privilege escalation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32167
- https://github.com/cloudreve/Cloudreve/commit/4b85541d73949969f41ad46d1e00544c9f1a7538
- https://github.com/cloudreve/Cloudreve
- https://github.com/cloudreve/Cloudreve/releases/tag/3.6.0-beta1
- https://www.mend.io/vulnerability-database/CVE-2022-32167
