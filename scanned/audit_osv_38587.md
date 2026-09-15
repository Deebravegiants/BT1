# [M] Horilla: Insecure Direct Object Reference at `/employee/view-file/<int:id>

## Summary
Severity: Medium
Advisory: CVE-2026-40865
Aliases: GHSA-85cj-fwjh-fjv7
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40865
Type: osv

## Details
Horilla is a free and open source Human Resource Management System (HRMS). In 1.5.0, an insecure direct object reference in the employee document viewer allows any authenticated user to access other employees’ uploaded documents by changing the document ID in the request. This exposes sensitive HR files such as identity documents, contracts, certificates, and other private employee records.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40865.json
- https://github.com/horilla/horilla-hr/security/advisories/GHSA-85cj-fwjh-fjv7
- https://nvd.nist.gov/vuln/detail/CVE-2026-40865
