# [M] MongoDB BI Connector ODBC driver may write outside an allocated buffer when retrieving large floating point values as character data

## Summary
Severity: Medium
Advisory: CVE-2026-18888
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-18888
Type: osv

## Details
The MongoDB BI Connector ODBC Driver converts floating point column values into text without checking that the result fits within the destination buffer. When an application reads a sufficiently large floating point value as text, the driver may write beyond the end of that buffer and corrupt adjacent memory. A user who can store data in a collection read through the BI Connector could use this to crash the application performing the read.

## References
- https://github.com/mongodb/mongo-bi-connector-odbc-driver/releases/tag/v1.4.9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/18xxx/CVE-2026-18888.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-18888
- https://github.com/mongodb/mongo-bi-connector-odbc-driver
