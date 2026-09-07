# [M] Cross-site scripting in Apache Ranger

## Summary
Severity: Medium
Advisory: GHSA-fpqp-v323-44xv
CVE: CVE-2019-12397
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-08-16
Source: https://github.com/advisories/GHSA-fpqp-v323-44xv
Type: github-advisory

## Affected
- Maven: `org.apache.ranger:ranger` — affected >=0.7.0 <2.0.0

## Details
Policy import functionality in Apache Ranger 0.7.0 to 1.2.0 is vulnerable to a cross-site scripting issue. Upgrade to 2.0.0 or later version of Apache Ranger with the fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12397
- https://cwiki.apache.org/confluence/display/RANGER/Vulnerabilities+found+in+Ranger
- https://lists.apache.org/thread.html/ab2de1adad96f5dbd19d976b28715dfc60dbe75e82a74f48be8ef695@%3Cdev.ranger.apache.org%3E
- https://lists.apache.org/thread.html/cbc6346708ef2b9ffb2555637311bf6294923c609c029389fa39de8f@%3Cdev.ranger.apache.org%3E
- http://www.openwall.com/lists/oss-security/2019/08/08/1
