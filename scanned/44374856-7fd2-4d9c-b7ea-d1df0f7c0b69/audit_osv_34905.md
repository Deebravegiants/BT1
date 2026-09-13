# [C] CVE-2025-66385

## Summary
Severity: Critical
Advisory: CVE-2025-66385
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-11-28
Source: https://osv.dev/vulnerability/CVE-2025-66385
Type: osv

## Details
UsersController::edit in Cerebrate before 1.30 allows an authenticated non-privileged user to escalate their privileges (e.g., obtain a higher role such as admin) via the user-edit endpoint by supplying or modifying role_id or organisation_id fields in the edit request.

## References
- https://github.com/cerebrate-project/cerebrate/compare/v1.29...v1.30
- https://vulnerability.circl.lu/api/vulnerability/gcve-1-2025-0017
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66385.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66385
- https://github.com/cerebrate-project/cerebrate/commit/c9bfa90abc85d4a20a9cc2f282959b72bef829bb
