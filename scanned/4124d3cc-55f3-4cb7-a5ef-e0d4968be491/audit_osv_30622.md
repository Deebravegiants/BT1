# [M] Course Roster vulnerable to CSV Injection in Autolab

## Summary
Severity: Medium
Advisory: CVE-2024-53260
Aliases: GHSA-cqxx-pfmh-h43g
CVSS: 6.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N)
Published: 2024-11-27
Source: https://osv.dev/vulnerability/CVE-2024-53260
Type: osv

## Details
Autolab is a course management service that enables auto-graded programming assignments. A user can modify their first and or last name to include a valid excel / spreadsheet formula. When an instructor downloads their course's roster and opens, this name will then be evaluated as a formula. This could lead to leakage of information of students in the course roster by sending the data to a remote endpoint. This issue has been patched in the source code repository and the fix is expected to be released in the next version. Users are advised to manually patch their systems or to wait for the next release. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53260.json
- https://github.com/autolab/Autolab/security/advisories/GHSA-cqxx-pfmh-h43g
- https://nvd.nist.gov/vuln/detail/CVE-2024-53260
- https://github.com/autolab/Autolab/commit/fe44b53815d37c63e751032205b692ccd5737620
