# [H] Improper Restriction of XML External Entity Reference in Apache FOP

## Summary
Severity: High
Advisory: GHSA-5hg8-r9vq-gjqp
CVE: CVE-2017-5661
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-5hg8-r9vq-gjqp
Type: github-advisory

## Affected
- Maven: `org.apache.xmlgraphics:fop` — affected >=0 <2.2

## Details
In Apache FOP before 2.2, files lying on the filesystem of the server which uses FOP can be revealed to arbitrary users who send maliciously formed SVG files. The file types that can be shown depend on the user context in which the exploitable application is running. If the user is root a full compromise of the server - including confidential or sensitive files - would be possible. XXE can also be used to attack the availability of the server via denial of service as the references within a xml document can trivially trigger an amplification attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5661
- https://www.tenable.com/security/tns-2021-14
- https://xmlgraphics.apache.org/security.html
- http://www.debian.org/security/2017/dsa-3864
- http://www.securityfocus.com/bid/97947
