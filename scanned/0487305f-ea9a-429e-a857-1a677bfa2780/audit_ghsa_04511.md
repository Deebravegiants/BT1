# [C] Apache CXF OAuth2 has Inverted IP Binding Check that Defeats Security Control

## Summary
Severity: Critical
Advisory: GHSA-g5v7-jchf-7jrr
CVE: CVE-2026-50628
CWE: CWE-20, CWE-358
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-g5v7-jchf-7jrr
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=4.2.0 <4.2.2
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=0 <4.1.7

## Details
A logic error in OAuthRequestFilter rejects legitimate requests originating from the bound IP address, while blindly allowing requests from any other IP address. Enabling this

security feature inadvertently creates an inverse security check. Users are recommended to upgrade to versions 4.2.2 or 4.1.7, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50628
- https://access.redhat.com/errata/RHSA-2026:37390
- https://access.redhat.com/security/cve/CVE-2026-50628
- https://bugzilla.redhat.com/show_bug.cgi?id=2488302
- https://github.com/apache/cxf
- https://lists.apache.org/thread/vb3ho8lf228gh90m1fpnohf2008xrdxk
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-50628.json
- http://www.openwall.com/lists/oss-security/2026/06/11/5
