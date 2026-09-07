# [H] Remote Code Execution vulnerability in Apache IoTDB via UDF

## Summary
Severity: High
Advisory: GHSA-rxgg-273w-rfw7
CVE: CVE-2023-46226
CWE: CWE-94
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-15
Source: https://github.com/advisories/GHSA-rxgg-273w-rfw7
Type: github-advisory

## Affected
- Maven: `org.apache.iotdb:iotdb-core` — affected >=1.0.0 <1.3.0
- PyPI: `apache-iotdb` — affected >=1.0.0 <1.3.0

## Details
Remote Code Execution vulnerability in Apache IoTDB. This issue affects Apache IoTDB from 1.0.0 through 1.2.2.

Users are recommended to upgrade to version 1.3.0, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46226
- https://github.com/apache/iotdb
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-iotdb/PYSEC-2024-11.yaml
- https://lists.apache.org/thread/293b4ob65ftnfwyf62fb9zh8gwdy38hg
- http://www.openwall.com/lists/oss-security/2024/01/15/1
