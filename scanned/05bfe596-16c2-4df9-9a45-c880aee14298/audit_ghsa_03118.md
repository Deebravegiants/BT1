# [M] Apache Livy Cross-site scripting (XSS) in session names

## Summary
Severity: Medium
Advisory: GHSA-74qp-233x-p5j8
CVE: CVE-2021-26544
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-13
Source: https://github.com/advisories/GHSA-74qp-233x-p5j8
Type: github-advisory

## Affected
- Maven: `org.apache.livy:livy-server` — affected >=0.7.0-incubating <0.7.1-incubating

## Details
Livy server version 0.7.0-incubating (only) is vulnerable to a cross site scripting issue in the session name. A malicious user could use this flaw to access logs and results of other users' sessions and run jobs with their privileges. This issue is fixed in Livy 0.7.1-incubating.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26544
- https://github.com/apache/incubator-livy/commit/4d8a912699683b973eee76d4e91447d769a0cb0d
- https://github.com/apache/incubator-livy/commit/9f1ba47a2f0d8accc435b133b42c3a76aa9ac846
- https://lists.apache.org/thread.html/r2db14e7fd1e5ec2519e8828d43529bad623d75698cc7918af3a3f3ed%40%3Cuser.livy.apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/02/20/1
