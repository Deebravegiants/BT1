# [M] CVE-2025-67081

## Summary
Severity: Medium
Advisory: CVE-2025-67081
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2025-67081
Type: osv

## Details
An SQL injection vulnerability in Itflow through 25.06 has been identified in the "role_id" parameter when editing a profile. An attacker with admin account can exploit this issue via blind SQL injection, allowing for the extraction of arbitrary data from the database. The vulnerability arises from insufficient sanitizing on integer parameter.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67081.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67081
- https://www.helx.io/blog/advisory-itflow/
- https://github.com/itflow-org/itflow
