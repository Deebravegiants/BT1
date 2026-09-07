# [M] Apache OpenMeetings Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-633w-w2pf-x84r
CVE: CVE-2016-3089
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-633w-w2pf-x84r
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=0 <3.1.2

## Details
Cross-site scripting (XSS) vulnerability in the SWF panel in Apache OpenMeetings before 3.1.2 allows remote attackers to inject arbitrary web script or HTML via the swf parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-3089
- https://github.com/apache/openmeetings
- https://www.apache.org/dist/openmeetings/3.1.2/CHANGELOG
- http://openmeetings.apache.org/security.html
- http://packetstormsecurity.com/files/138313/Apache-OpenMeetings-3.1.0-Cross-Site-Scripting.html
- http://www.securityfocus.com/archive/1/539192/100/0/threaded
- http://www.securityfocus.com/bid/92442
