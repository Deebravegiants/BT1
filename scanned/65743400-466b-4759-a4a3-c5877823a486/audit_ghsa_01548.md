# [C] Command Injection in Kylin

## Summary
Severity: Critical
Advisory: GHSA-qwfw-gxx2-mmv2
CVE: CVE-2020-13925
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-qwfw-gxx2-mmv2
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin-server-base` — affected >=0 <3.1.0

## Details
Similar to CVE-2020-1956, Kylin has one more restful API which concatenates the API inputs into OS commands and then executes them on the server; while the reported API misses necessary input validation, which causes the hackers to have the possibility to execute OS command remotely. Users of all previous versions after 2.3 should upgrade to 3.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13925
- https://lists.apache.org/thread.html/r021baf9d8d4ae41e8c8332c167c4fa96c91b5086563d9be55d2d7acf@%3Ccommits.kylin.apache.org%3E
- https://lists.apache.org/thread.html/r250a867961cfd6e0506240a9c7eaee782d84c6ab0091c7c4bc45f3eb%40%3Cuser.kylin.apache.org%3E
- https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEKYLIN-584373
