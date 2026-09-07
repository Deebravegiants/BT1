# [H] Apache OpenMeetings vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-m5pm-rgvf-vg22
CVE: CVE-2017-7666
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-m5pm-rgvf-vg22
Type: github-advisory

## Affected
- Maven: `org.apache.openmeetings:openmeetings-parent` — affected >=1.0.0 <3.3.0

## Details
Apache OpenMeetings 1.0.0 is vulnerable to Cross-Site Request Forgery (CSRF) attacks, XSS attacks, click-jacking, and MIME based attacks. The issue is fixed in version 3.3.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7666
- https://github.com/apache/openmeetings
- http://markmail.org/message/fkesu4e5hhz5xdbg
