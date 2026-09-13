# [C] H2O Deserialization of Untrusted Data Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h7xg-cmpp-48hf
CVE: CVE-2024-10553
CWE: CWE-502
Ecosystem: Maven, PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-h7xg-cmpp-48hf
Type: github-advisory

## Affected
- PyPI: `h2o` — affected >=0 <3.46.0.6
- Maven: `ai.h2o:h2o-core` — affected >=0 <3.46.0.6

## Details
A vulnerability in the h2oai/h2o-3 REST API versions 3.46.0.4 allows unauthenticated remote attackers to execute arbitrary code via deserialization of untrusted data. The vulnerability exists in the endpoints POST /99/ImportSQLTable and POST /3/SaveToHiveTable, where user-controlled JDBC URLs are passed to DriverManager.getConnection, leading to deserialization if a MySQL or PostgreSQL driver is available in the classpath. This issue is fixed in version 3.46.0.6.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-10553
- https://github.com/h2oai/h2o-3/commit/ac1d642b4d86f10a02d75974055baf2a4b2025ac
- https://github.com/h2oai/h2o-3
- https://huntr.com/bounties/e6f550dd-eda2-428c-a740-ed8f893a084b
