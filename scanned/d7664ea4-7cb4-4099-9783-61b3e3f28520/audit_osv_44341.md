# [C] BI Connector ODBC Driver Improper Bounds Checking on Cursor Name Leading to Memory Corruption

## Summary
Severity: Critical
Advisory: CVE-2026-81532
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-81532
Type: osv

## Details
A user able to submit SQL through an application using the MongoDB Connector for BI ODBC driver can supply a positioned-cursor statement whose cursor name exceeds the size of an internal fixed-length buffer. Because the name length is not bounded before the driver builds its diagnostic message, memory adjacent to that buffer is overwritten with user-supplied content. This can terminate the hosting application process and may allow unintended code to run within it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81532.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81532
- https://github.com/mongodb/mongo-bi-connector-odbc-driver/releases
