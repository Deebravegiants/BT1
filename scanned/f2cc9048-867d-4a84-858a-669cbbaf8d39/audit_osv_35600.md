# [M] MISP user edit endpoint mass assignment vulnerability allows unauthorized user account modification

## Summary
Severity: Medium
Advisory: CVE-2026-10868
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:H/SA:N)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-10868
Type: osv

## Details
A mass assignment vulnerability exists in the MISP user edit functionality due to insufficient filtering of user-supplied fields in UsersController::edit(). When processing edit requests, the application accepted a user-controlled User.id value from request data. An authenticated attacker could craft a modified request containing another user identifier, potentially causing updates to be applied to an unintended user account. Depending on the editable fields and the attacker’s privileges, this could allow unauthorized modification of user account attributes and impact account integrity.



The issue was addressed by explicitly removing the User.id field from request data before processing the user edit operation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10868.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10868
- https://github.com/MISP/MISP/commit/1be8c413b7104a889dfd30c5b1986e3ab17238e8
