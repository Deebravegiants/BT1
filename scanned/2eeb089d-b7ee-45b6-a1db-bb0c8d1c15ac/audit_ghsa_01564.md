# [H] Command Injection in Kylin

## Summary
Severity: High
Advisory: GHSA-gprm-xqrc-c2j3
CVE: CVE-2020-1956
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-gprm-xqrc-c2j3
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin-core-common` — affected >=0 <2.6.6
- Maven: `org.apache.kylin:kylin-core-common` — affected >=3.0.0 <3.0.2

## Details
Kylin has some restful apis which will concatenate os command with the user input string, a user is likely to be able to execute any os command without any protection or validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1956
- https://github.com/apache/kylin/commit/58fad56ac6aaa43c6bd8f962d7f2d84438664092
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-1956
- https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEKYLIN-570207
- https://lists.apache.org/thread.html/r61666760d8a4e8764b2d5fe158d8a48b569414480fbfadede574cdc0@%3Ccommits.kylin.apache.org%3E
- https://lists.apache.org/thread.html/r61666760d8a4e8764b2d5fe158d8a48b569414480fbfadede574cdc0%40%3Ccommits.kylin.apache.org%3E
- https://lists.apache.org/thread.html/r250a867961cfd6e0506240a9c7eaee782d84c6ab0091c7c4bc45f3eb@%3Cuser.kylin.apache.org%3E
- https://lists.apache.org/thread.html/r250a867961cfd6e0506240a9c7eaee782d84c6ab0091c7c4bc45f3eb@%3Cdev.kylin.apache.org%3E
- https://lists.apache.org/thread.html/r250a867961cfd6e0506240a9c7eaee782d84c6ab0091c7c4bc45f3eb@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r250a867961cfd6e0506240a9c7eaee782d84c6ab0091c7c4bc45f3eb%40%3Cuser.kylin.apache.org%3E
- https://lists.apache.org/thread.html/r250a867961cfd6e0506240a9c7eaee782d84c6ab0091c7c4bc45f3eb%40%3Cdev.kylin.apache.org%3E
- https://lists.apache.org/thread.html/r250a867961cfd6e0506240a9c7eaee782d84c6ab0091c7c4bc45f3eb%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/r1332ef34cf8e2c0589cf44ad269fb1fb4c06addec6297f0320f5111d%40%3Cuser.kylin.apache.org%3E
- https://lists.apache.org/thread.html/r021baf9d8d4ae41e8c8332c167c4fa96c91b5086563d9be55d2d7acf@%3Ccommits.kylin.apache.org%3E
- https://lists.apache.org/thread.html/r021baf9d8d4ae41e8c8332c167c4fa96c91b5086563d9be55d2d7acf%40%3Ccommits.kylin.apache.org%3E
- https://github.com/apache/kylin
- https://community.sonarsource.com/t/apache-kylin-3-0-1-command-injection-vulnerability/25706
- http://www.openwall.com/lists/oss-security/2020/07/14/1
