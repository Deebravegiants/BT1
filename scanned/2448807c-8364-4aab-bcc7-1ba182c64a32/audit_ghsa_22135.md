# [H] Unrestricted Upload of File with Dangerous Type in Sonatype Nexus Repository Manager

## Summary
Severity: High
Advisory: GHSA-hmjv-px3j-933c
CVE: CVE-2019-16530
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hmjv-px3j-933c
Type: github-advisory

## Affected
- Maven: `org.sonatype.nexus:nexus-repository` — affected >=2.0.0 <2.14.15
- Maven: `org.sonatype.nexus:nexus-repository` — affected >=3.0.0 <3.19.0

## Details
Sonatype Nexus Repository Manager 2.x before 2.14.15 and 3.x before 3.19, and IQ Server before 72, has remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16530
- https://issues.sonatype.org/secure/ReleaseNote.jspa
- https://support.sonatype.com/hc/en-us/articles/360036132453
