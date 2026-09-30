# [C] MongoDB BI Connector ODBC Driver Memory-Safety Issue When Handling Stored Procedure Output Parameters

## Summary
Severity: Critical
Advisory: CVE-2026-19004
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-19004
Type: osv

## Details
An application using the MongoDB BI Connector ODBC Driver may experience a memory-safety issue when processing output parameters from a stored procedure. Triggering this issue requires connecting to an untrusted or impersonated database server that returns crafted metadata. This may result in process termination, disclosure of process memory, or, under certain conditions, arbitrary code execution.

## References
- https://github.com/mongodb/mongo-bi-connector-odbc-driver/releases/tag/v1.4.9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19004.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19004
- https://github.com/mongodb/mongo-bi-connector-odbc-driver
