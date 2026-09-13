# [M] Observable Response Discrepancy in Kibana Leading to Cross-Space Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-78584
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-78584
Type: osv

## Details
Observable Response Discrepancy (CWE-204) in the Kibana Osquery feature can lead to information disclosure via Query System for Information (CAPEC-54). An authenticated user holding Osquery live-query privileges could determine whether a scheduled query identifier exists in a Kibana space they are not authorized to access.

## References
- https://discuss.elastic.co/t/kibana-9-4-4-security-update-esa-2026-161/390115
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78584.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78584
