# [H] CVE-2026-51956

## Summary
Severity: High
Advisory: CVE-2026-51956
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-51956
Type: osv

## Details
A Broken Object Level Authorization vulnerability exists in Grashjs Atlas CMMS prior to v1.6.0. An authenticated user from one tenant can read and modify another tenant's company record by changing only the numeric ID in the /company/{id} endpoint. The application does not enforce tenant-level ownership checks when accessing or updating company objects, allowing cross-tenant access and modification of company profile data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/51xxx/CVE-2026-51956.json
- https://github.com/h4vrut4/security-advisories/blob/main/CVE-2026-51956.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-51956
- https://github.com/Grashjs/cmms/commit/283bbc985cda497d6b592faae45ae1dbc8d53966
- https://github.com/Grashjs/cmms
