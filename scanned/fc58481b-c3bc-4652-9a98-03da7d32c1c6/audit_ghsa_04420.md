# [C] Apache CXF OAuth2 Missing JWT Audience and Issuer Validation in Access Token Validator

## Summary
Severity: Critical
Advisory: GHSA-9mrv-8pvf-hf4m
CVE: CVE-2026-50627
CWE: CWE-289, CWE-303
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-9mrv-8pvf-hf4m
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=4.2.0 <4.2.2
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=0 <4.1.7

## Details
The JwtAccessTokenValidator class in Apache CXF fails to validate the 'aud' (Audience) claims of incoming JWT access tokens. This allows a JWT issued for one Resource Server to be successfully replayed against a completely different Resource Server, leading to Token Confusion/Routing attacks. Users are recommended to upgrade to versions 4.2.2 or 4.1.7, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50627
- https://access.redhat.com/errata/RHSA-2026:37390
- https://access.redhat.com/security/cve/CVE-2026-50627
- https://bugzilla.redhat.com/show_bug.cgi?id=2488298
- https://github.com/apache/cxf
- https://lists.apache.org/thread/0jfzz9q992957b99tw7hodcqjfyxwb1m
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-50627.json
- http://www.openwall.com/lists/oss-security/2026/06/11/4
