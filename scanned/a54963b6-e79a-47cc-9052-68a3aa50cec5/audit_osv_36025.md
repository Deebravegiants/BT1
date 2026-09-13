# [C] Crafted database metadata may cause memory corruption in MongoDB BI Connector ODBC Driver

## Summary
Severity: Critical
Advisory: CVE-2026-19002
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-19002
Type: osv

## Details
A missing bounds check when parsing stored procedure parameter metadata in the MongoDB BI Connector ODBC Driver can result in an out-of-bounds write in the client application process. Triggering this issue requires control over the server the driver connects to, or the ability to respond in its place, in order to return malformed metadata. The resulting memory corruption may cause the client application to terminate abnormally or, under certain conditions, execute unintended code.

## References
- https://github.com/mongodb/mongo-bi-connector-odbc-driver/releases/tag/v1.4.9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19002.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19002
- https://github.com/mongodb/mongo-bi-connector-odbc-driver
