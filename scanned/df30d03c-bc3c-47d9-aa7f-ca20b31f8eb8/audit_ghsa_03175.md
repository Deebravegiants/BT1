# [C] SQL Injection in Apache SkyWalking

## Summary
Severity: Critical
Advisory: GHSA-grpf-gg7v-5g5h
CVE: CVE-2020-13921
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-grpf-gg7v-5g5h
Type: github-advisory

## Affected
- Maven: `org.apache.skywalking:oap-server` — affected >=0 <8.1.0

## Details
Only when using H2/MySQL/TiDB as Apache SkyWalking storage, there is a SQL injection vulnerability in the wildcard query cases.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13921
- https://github.com/apache/skywalking/pull/4970
- https://github.com/apache/skywalking/commit/fb7912c6bdda06a233f4b3e18e71a87d3e4a8951
- https://github.com/apache/skywalking
- https://github.com/pypa/advisory-database/tree/main/vulns/apache-skywalking/PYSEC-2020-342.yaml
- https://lists.apache.org/thread.html/r6f3a934ebc54585d8468151a494c1919dc1ee2cccaf237ec434dbbd6%40%3Cdev.skywalking.apache.org%3E
- https://lists.apache.org/thread.html/r6f3a934ebc54585d8468151a494c1919dc1ee2cccaf237ec434dbbd6@%3Cdev.skywalking.apache.org%3E
- http://www.openwall.com/lists/oss-security/2020/08/05/3
