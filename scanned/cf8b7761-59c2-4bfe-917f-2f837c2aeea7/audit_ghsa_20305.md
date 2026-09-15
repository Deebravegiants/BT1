# [M] Log Injection in Apache Sling Commons Log and Apache Sling API

## Summary
Severity: Medium
Advisory: GHSA-qmx3-m648-hr74
CVE: CVE-2022-32549
CWE: CWE-116, CWE-117
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-06-23
Source: https://github.com/advisories/GHSA-qmx3-m648-hr74
Type: github-advisory

## Affected
- Maven: `org.apache.sling:org.apache.sling.commons.log` — affected >=0
- Maven: `org.apache.sling:org.apache.sling.api` — affected >=0

## Details
Apache Sling Commons Log <= 5.4.0 and Apache Sling API <= 2.25.0 are vulnerable to log injection. The ability to forge logs may allow an attacker to cover tracks by injecting fake logs and potentially corrupt log files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-32549
- https://lists.apache.org/thread/7z6h3806mwcov5kx6l96pq839sn0po1v
