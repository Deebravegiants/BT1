# [H] trentm/json vulnerable to command injection

## Summary
Severity: High
Advisory: GHSA-3c6g-pvg8-gqw2
CVE: CVE-2020-7712
CWE: CWE-78
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-3c6g-pvg8-gqw2
Type: github-advisory

## Affected
- npm: `json` — affected >=0 <10.0.0
- Maven: `org.webjars.npm:json` — affected >=0

## Details
This affects the package json before 10.0.0. It is possible to inject arbritary commands using the parseLookup function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7712
- https://github.com/trentm/json/issues/144
- https://github.com/trentm/json/pull/145
- https://github.com/trentm/json/commit/cc4798169f9e0f181f8aa61905b88479badcd483
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://snyk.io/vuln/SNYK-JS-JSON-597481
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-608931
- https://lists.apache.org/thread.html/ree3abcd33c06ee95ab59faa1751198a1186d8941ddc2c2562c12966c@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rec8bb4d637b04575da41cfae49118e108e95d43bfac39b7b698ee4db@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rd9b9cc843f5cf5b532bdad9e87a817967efcf52b917e8c43b6df4cc7@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rba7ea4d75d6a8e5b935991d960d9b893fd30e576c4d3b531084ebd7d@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/rb89bd82dffec49f83b49e9ad625b1b63a408b3c7d1a60d6f049142a0@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/rb2b981912446a74e14fe6076c4b7c7d8502727ea0718e6a65a9b1be5@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rb023d54a46da1ac0d8969097f5fecc79636b07d3b80db7b818a5c55c@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ra890c24b3d90be36daf48ae76b263acb297003db24c1122f8e4aaef2@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r9c6d28e5b9a9b3481b7d1f90f1c2f75cd1a5ade91038426e0fb095da@%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/r977a907ecbedf87ae5ba47d4c77639efb120f74d4d1b3de14a4ef4da@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r8d2e174230f6d26e16c007546e804c343f1f68956f526daaafa4aaae@%3Cdev.zookeeper.apache.org%3E
