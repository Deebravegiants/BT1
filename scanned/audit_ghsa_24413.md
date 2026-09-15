# [H] Improper Input Validation in Apache Commons Email

## Summary
Severity: High
Advisory: GHSA-p7vm-phxx-g722
CVE: CVE-2017-9801
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-p7vm-phxx-g722
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-email` — affected >=1.0 <1.5

## Details
When a call-site passes a subject for an email that contains line-breaks in Apache Commons Email 1.0 through 1.4, the caller can add arbitrary SMTP headers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-9801
- https://lists.apache.org/thread.html/7ef903a772a2ff08605df1be819044fb15df2815eb3d63878b3fbbb5@%3Cannounce.apache.org%3E
- http://www.securityfocus.com/bid/100082
- http://www.securitytracker.com/id/1039043
