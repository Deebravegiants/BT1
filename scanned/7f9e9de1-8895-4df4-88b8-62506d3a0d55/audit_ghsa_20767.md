# [H] Apache IoTDB grafana-connector contains an interface without authorization

## Summary
Severity: High
Advisory: GHSA-c86f-9grv-pmqf
CVE: CVE-2022-38370
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-06
Source: https://github.com/advisories/GHSA-c86f-9grv-pmqf
Type: github-advisory

## Affected
- Maven: `org.apache.iotdb:iotdb-grafana-connector` — affected >=0 <0.13.1

## Details
Apache IoTDB grafana-connector version 0.13.0 contains an interface without authorization, which may expose the internal structure of a database. Users should upgrade to version 0.13.1, which addresses this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38370
- https://github.com/apache/iotdb
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-iotdb/PYSEC-2022-43070.yaml
- https://lists.apache.org/thread/kcpqgstvgf8sxy9ktxm1836nlwc8xy3j
- http://www.openwall.com/lists/oss-security/2022/09/05/2
