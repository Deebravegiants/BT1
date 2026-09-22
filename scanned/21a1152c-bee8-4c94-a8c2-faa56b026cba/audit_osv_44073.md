# [M] Incorrect Authorization in Kibana Leading to Unauthorized Disclosure, Modification, and Deletion of Data

## Summary
Severity: Medium
Advisory: CVE-2026-78606
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-78606
Type: osv

## Details
Incorrect Authorization (CWE-863) in Kibana can lead to unauthorized disclosure, modification, and deletion of data via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1). Where two authenticated principals originating from different authentication realms share the same username value, one could read, modify, and delete the other's private Elastic AI Assistant Knowledge Base entries.

## References
- https://discuss.elastic.co/t/kibana-8-19-21-9-4-6-9-5-2-security-update-esa-2026-142/390093
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78606.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78606
