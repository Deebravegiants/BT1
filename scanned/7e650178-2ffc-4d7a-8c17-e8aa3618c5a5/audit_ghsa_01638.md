# [H] Improper input validation in Apache Shiro

## Summary
Severity: High
Advisory: GHSA-r679-m633-g7wc
CVE: CVE-2019-12422
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-02-04
Source: https://github.com/advisories/GHSA-r679-m633-g7wc
Type: github-advisory

## Affected
- Maven: `org.apache.shiro:shiro-core` — affected >=0 <1.4.2

## Details
Apache Shiro before 1.4.2, when using the default "remember me" configuration, cookies could be susceptible to a padding attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12422
- https://lists.apache.org/thread.html/c9db14cfebfb8e74205884ed2bf2e2b30790ce24b7dde9191c82572c@%3Cdev.shiro.apache.org%3E
- https://lists.apache.org/thread.html/r2d2612c034ab21a3a19d2132d47d3e4aa70105008dd58af62b653040@%3Ccommits.shiro.apache.org%3E
