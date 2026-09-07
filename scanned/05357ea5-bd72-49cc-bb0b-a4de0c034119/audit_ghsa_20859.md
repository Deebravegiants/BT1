# [M] Apache IoTDB Session Fixation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g6vm-3ch8-c6jq
CVE: CVE-2022-38369
CWE: CWE-384
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-06
Source: https://github.com/advisories/GHSA-g6vm-3ch8-c6jq
Type: github-advisory

## Affected
- Maven: `org.apache.iotdb:iotdb-server` — affected >=0 <0.13.1
- PyPI: `apache-iotdb` — affected >=0 <0.13.1

## Details
Apache IoTDB version 0.13.0 is vulnerable to session id attack. Users should upgrade to version 0.13.1 which addresses this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38369
- https://github.com/apache/iotdb
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-iotdb/PYSEC-2022-43069.yaml
- https://lists.apache.org/thread/7nk03ywvx3t3yjbcxzt7zy4nyc89y9b0
- http://www.openwall.com/lists/oss-security/2022/09/05/1
