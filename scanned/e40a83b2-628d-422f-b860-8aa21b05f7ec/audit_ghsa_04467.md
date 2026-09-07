# [H] Apache CXF OAuth2 TOCTOU Race Condition in Refresh Token Processing

## Summary
Severity: High
Advisory: GHSA-83r6-96m8-r52p
CVE: CVE-2026-50631
CWE: CWE-367
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-83r6-96m8-r52p
Type: github-advisory

## Affected
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=4.2.0 <4.2.2
- Maven: `org.apache.cxf:cxf-rt-rs-security-oauth2` — affected >=0 <4.1.7

## Details
A race condition in AbstractOAuthDataProvider allows concurrent requests using the same Refresh Token to bypass single-use semantics and generate multiple valid Access Tokens, when 'recycleRefreshTokens' is set to false. A leaked refresh token can be replayed concurrently by multiple attackers or threads. Users are recommended to upgrade to versions 4.2.2 or 4.1.7, which fixes this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-50631
- https://github.com/apache/cxf
- https://lists.apache.org/thread/s83t3x4r626o9h8rt0ryr1w7w53l1vv8
- http://www.openwall.com/lists/oss-security/2026/06/11/8
