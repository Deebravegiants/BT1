# [M] Incorrect Authorization in Kibana Leading to Unauthorized Modification of Data

## Summary
Severity: Medium
Advisory: CVE-2026-72641
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-72641
Type: osv

## Details
Incorrect Authorization (CWE-863) in Kibana can lead to unauthorized modification of data via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1). An authenticated user holding only Security Solution read access in a Kibana space could enumerate and change the state of Entity Store maintainer tasks, silently disabling Entity Analytics maintenance for that space.

## References
- https://discuss.elastic.co/t/kibana-9-4-6-9-5-1-security-update-esa-2026-122/390089
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72641.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72641
