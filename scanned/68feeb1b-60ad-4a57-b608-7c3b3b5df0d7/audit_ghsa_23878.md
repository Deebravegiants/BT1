# [H] Improper Restriction of XML External Entity Reference in Apache Batik

## Summary
Severity: High
Advisory: GHSA-qwgx-59jw-qfg9
CVE: CVE-2017-5662
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qwgx-59jw-qfg9
Type: github-advisory

## Affected
- Maven: `org.apache.xmlgraphics:batik` — affected >=0 <1.9

## Details
In Apache Batik before 1.9, files lying on the filesystem of the server which uses batik can be revealed to arbitrary users who send maliciously formed SVG files. The file types that can be shown depend on the user context in which the exploitable application is running. If the user is root a full compromise of the server - including confidential or sensitive files - would be possible. XXE can also be used to attack the availability of the server via denial of service as the references within a xml document can trivially trigger an amplification attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5662
- https://access.redhat.com/errata/RHSA-2017:2546
- https://access.redhat.com/errata/RHSA-2017:2547
- https://access.redhat.com/errata/RHSA-2018:0319
- https://www.debian.org/security/2018/dsa-4215
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://xmlgraphics.apache.org/security.html
- http://www.oracle.com/technetwork/security-advisory/cpuapr2018-3678067.html
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- http://www.securityfocus.com/bid/97948
- http://www.securitytracker.com/id/1038334
