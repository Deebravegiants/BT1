# [M] Missing Authorization in Harbor

## Summary
Severity: Medium
Advisory: GHSA-9wvh-ff5f-xjpj
CVE: CVE-2019-16097
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-9wvh-ff5f-xjpj
Type: github-advisory

## Affected
- Go: `github.com/goharbor/harbor` — affected >=1.7.0 <1.9.0-rc1

## Details
core/api/user.go in Harbor 1.7.0 through 1.8.2 allows non-admin users to create admin accounts via the POST /api/users API. This is fixed in 1.9.0-rc1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16097
- https://github.com/goharbor/harbor/commit/b6db8a8a106259ec9a2c48be8a380cb3b37cf517
- https://github.com/goharbor/harbor/compare/v1.8.2...v1.9.0-rc1
- https://github.com/goharbor/harbor/releases/tag/v1.7.6
- https://github.com/goharbor/harbor/releases/tag/v1.8.3
- https://github.com/ianxtianxt/CVE-2019-16097
- https://unit42.paloaltonetworks.com/critical-vulnerability-in-harbor-enables-privilege-escalation-from-zero-to-admin-cve-2019-16097
- http://www.vmware.com/security/advisories/VMSA-2019-0015.html
