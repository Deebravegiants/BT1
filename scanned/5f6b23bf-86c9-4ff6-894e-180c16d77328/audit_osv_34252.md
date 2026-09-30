# [C] Deserialization Vulnerability in h2oai/h2o-3

## Summary
Severity: Critical
Advisory: CVE-2025-5662
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-02
Source: https://osv.dev/vulnerability/CVE-2025-5662
Type: osv

## Details
A deserialization vulnerability exists in the H2O-3 REST API (POST /99/ImportSQLTable) that affects all versions up to 3.46.0.7. This vulnerability allows remote code execution (RCE) due to improper validation of JDBC connection parameters when using a Key-Value format. The vulnerability is present in the MySQL JDBC Driver version 8.0.19 and JDK version 8u112. The issue is resolved in version 3.46.0.8.

## References
- https://huntr.com/bounties/057a743b-b2ec-4312-8262-ce0ff8bc161c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5662.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5662
- https://github.com/h2oai/h2o-3/commit/f714edd6b8429c7a7211b779b6ec108a95b7382d
