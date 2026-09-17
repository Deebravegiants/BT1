# [M] Apache IoTDB Discloses Sensitive Information via Log Files

## Summary
Severity: Medium
Advisory: GHSA-5fc3-pqf2-57cx
CVE: CVE-2025-26864
CWE: CWE-200
Ecosystem: Maven, PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2025-05-14
Source: https://github.com/advisories/GHSA-5fc3-pqf2-57cx
Type: github-advisory

## Affected
- Maven: `org.apache.iotdb:node-commons` — affected >=0.10.0 <1.3.4
- Maven: `org.apache.iotdb:node-commons` — affected >=2.0.1-beta <2.0.2
- PyPI: `apache-iotdb` — affected >=0.10.0 <1.3.4
- PyPI: `apache-iotdb` — affected >=2.0.1b0 <2.0.2

## Details
Exposure of Sensitive Information to an Unauthorized Actor, Insertion of Sensitive Information into Log File vulnerability in the OpenIdAuthorizer of Apache IoTDB.

This issue affects Apache IoTDB: from 0.10.0 through 1.3.3, from 2.0.1-beta before 2.0.2.

Users are recommended to upgrade to version 1.3.4 and 2.0.2, which fix the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-26864
- https://github.com/apache/iotdb/pull/14863
- https://github.com/apache/iotdb/commit/34fcaff6b72470d5ad369307dde7fae8897aea7e
- https://github.com/apache/iotdb
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-iotdb/PYSEC-2025-60.yaml
- https://lists.apache.org/thread/2kcjnlypppk8qjh17dpz0jvkcpn6l162
- http://www.openwall.com/lists/oss-security/2025/05/14/4
