# [M] Improper Neutralization of Special Elements in Data Query Logic in Kibana Leading to Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-63138
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-63138
Type: osv

## Details
Improper Neutralization of Special Elements in Data Query Logic (CWE-943) in Kibana can lead to information disclosure via NoSQL Injection (CAPEC-676). An authenticated user with access to the affected query functionality could submit specially crafted input that alters the intended query logic, returning data the user is not authorized to read.

## References
- https://discuss.elastic.co/t/kibana-9-4-5-9-5-1-security-update-esa-2026-168/390082
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63138.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63138
