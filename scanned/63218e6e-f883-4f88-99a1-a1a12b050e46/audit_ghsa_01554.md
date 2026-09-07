# [M] SQL Injection in Kylin

## Summary
Severity: Medium
Advisory: GHSA-7hmh-8gwv-mfvq
CVE: CVE-2020-1937
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-07-27
Source: https://github.com/advisories/GHSA-7hmh-8gwv-mfvq
Type: github-advisory

## Affected
- Maven: `org.apache.kylin:kylin-server-base` — affected >=0 <2.6.5
- Maven: `org.apache.kylin:kylin-server-base` — affected >=3.0.0 <3.0.1

## Details
Kylin has some restful apis which will concatenate SQLs with the user input string, a user is likely to be able to run malicious database queries.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1937
- https://github.com/apache/kylin/commit/e373c64c96a54a7abfe4bccb82e8feb60db04749
- https://github.com/apache/kylin
- https://lists.apache.org/thread.html/r021baf9d8d4ae41e8c8332c167c4fa96c91b5086563d9be55d2d7acf@%3Ccommits.kylin.apache.org%3E
- https://lists.apache.org/thread.html/r61666760d8a4e8764b2d5fe158d8a48b569414480fbfadede574cdc0@%3Ccommits.kylin.apache.org%3E
- https://lists.apache.org/thread.html/rc574fef23740522f62ab3bbda4f6171be98aa7a25f3f54be143a80a8%40%3Cuser.kylin.apache.org%3E
- https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEKYLIN-552148
