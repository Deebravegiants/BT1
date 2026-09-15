# [H] Jenkins Active Directory Plugin did not verify certificate of AD server

## Summary
Severity: High
Advisory: GHSA-vcgj-j8c5-2h52
CVE: CVE-2017-2649
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vcgj-j8c5-2h52
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:active-directory` — affected >=0 <2.3

## Details
It was found that the Active Directory Plugin for Jenkins up to and including version 2.2 did not verify certificates of the Active Directory server, thereby enabling Man-in-the-Middle attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2649
- https://jenkins.io/security/advisory/2017-03-20
- http://www.securityfocus.com/bid/96986
