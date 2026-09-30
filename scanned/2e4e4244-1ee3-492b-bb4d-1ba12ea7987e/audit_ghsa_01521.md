# [C] SQL Injection in Kylin

## Summary
Severity: Critical
Advisory: GHSA-hx5g-8hq2-8x4w
CVE: CVE-2020-13926
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-hx5g-8hq2-8x4w
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin-server-base` — affected >=0 <3.1.0

## Details
Kylin concatenates and executes a Hive SQL in Hive CLI or beeline when building a new segment; some part of the HQL is from system configurations, while the configuration can be overwritten by certain rest api, which makes SQL injection attack is possible. Users of all previous versions after 2.0 should upgrade to 3.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13926
- https://lists.apache.org/thread.html/r021baf9d8d4ae41e8c8332c167c4fa96c91b5086563d9be55d2d7acf@%3Ccommits.kylin.apache.org%3E
- https://lists.apache.org/thread.html/r63d5663169e866d44ff9250796193337cff7d9cf61cc3839e86163fd%40%3Cuser.kylin.apache.org%3E
- https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEKYLIN-584374
