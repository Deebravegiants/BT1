# [C] Improper Restriction of Recursive Entity References in Apache XMLBeans

## Summary
Severity: Critical
Advisory: GHSA-mw3r-pfmg-xp92
CVE: CVE-2021-23926
CWE: CWE-776
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-mw3r-pfmg-xp92
Type: github-advisory

## Affected
- Maven: `org.apache.xmlbeans:xmlbeans` — affected >=0 <3.0.0

## Details
The XML parsers used by XMLBeans up to version 2.6.0 did not set the properties needed to protect the user from malicious XML input. Vulnerabilities include possibilities for XML Entity Expansion attacks. Affects XMLBeans up to and including v2.6.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23926
- https://issues.apache.org/jira/browse/XMLBEANS-517
- https://lists.apache.org/thread.html/r2dc5588009dc9f0310b7382269f932cc96cae4c3901b747dda1a7fed@%3Cjava-dev.axis.apache.org%3E
- https://lists.apache.org/thread.html/rbb01d10512098894cd5f22325588197532c64f1c818ea7e4120d40c1@%3Cjava-dev.axis.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2021/06/msg00024.html
- https://poi.apache.org
- https://security.netapp.com/advisory/ntap-20210513-0004
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
