# [M] MongoDB BI Connector ODBC Driver Memory-Safety Issue When Parsing Oversized LIMIT Values

## Summary
Severity: Medium
Advisory: CVE-2026-81533
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-81533
Type: osv

## Details
An application using the MongoDB BI Connector ODBC Driver may encounter a memory-safety issue when a submitted SQL statement contains an unusually long run of digits following a LIMIT clause. The issue occurs only on connections where the driver's optional prefetch setting is enabled, and stems from the driver copying the digit sequence into a fixed-size internal buffer without checking its length. A user able to influence the numeric portion of a LIMIT clause could cause the hosting application process to terminate unexpectedly or corrupt adjacent memory in that process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81533.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81533
- https://github.com/mongodb/mongo-bi-connector-odbc-driver/releases
