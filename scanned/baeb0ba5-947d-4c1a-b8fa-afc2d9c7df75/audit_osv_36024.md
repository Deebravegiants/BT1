# [C] MongoDB BI Connector ODBC driver may write outside an allocated buffer when handling oversized catalog object names

## Summary
Severity: Critical
Advisory: CVE-2026-19001
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-19001
Type: osv

## Details
The MongoDB BI Connector ODBC Driver may write outside the bounds of a fixed-size buffer when an application supplies an unusually long catalog, schema, or object name to a metadata retrieval function. This may result in memory corruption within the calling application's process, leading to abnormal termination and, under certain conditions, the potential for arbitrary code execution.

## References
- https://github.com/mongodb/mongo-bi-connector-odbc-driver/releases/tag/v1.4.9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19001.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19001
- https://github.com/mongodb/mongo-bi-connector-odbc-driver
