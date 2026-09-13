# [C] Apache IoTDB Vulnerable to Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-f4rq-f4j9-f6rm
CVE: CVE-2024-24780
CWE: CWE-94
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-f4rq-f4j9-f6rm
Type: github-advisory

## Affected
- Maven: `org.apache.iotdb:iotdb-core` — affected >=1.0.0 <1.3.4
- PyPI: `apache-iotdb` — affected >=1.0.0 <1.3.4

## Details
Remote Code Execution with untrusted URI of UDF vulnerability in Apache IoTDB. The attacker who has privilege to create UDF can register malicious function from untrusted URI.

This issue affects Apache IoTDB: from 1.0.0 before 1.3.4.

Users are recommended to upgrade to version 1.3.4, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24780
- https://github.com/apache/iotdb/pull/14365
- https://github.com/apache/iotdb
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-iotdb/PYSEC-2025-59.yaml
- https://lists.apache.org/thread/xphtm98v3zsk9vlpfh481m1ry2ctxvmj
- http://www.openwall.com/lists/oss-security/2025/05/14/2
