# [M] Improper file downloads in Apache Tapestry

## Summary
Severity: Medium
Advisory: GHSA-w9mp-p2wp-2xf7
CVE: CVE-2020-13953
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-w9mp-p2wp-2xf7
Type: github-advisory

## Affected
- Maven: `org.apache.tapestry:tapestry-core` — affected >=5.4.0 <5.6.0

## Details
In Apache Tapestry from 5.4.0 to 5.5.0, crafting specific URLs, an attacker can download files inside the WEB-INF folder of the WAR being run.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13953
- https://lists.apache.org/thread.html/r37dab61fc7f7088d4311e7f995ef4117d58d86a675f0256caa6991eb@%3Cusers.tapestry.apache.org%3E
- https://lists.apache.org/thread.html/r50eb12e8a12074a9b7ed63cbab91d180d19cc23dc1da3ed5b6e1280f%40%3Cusers.tapestry.apache.org%3E
