# [H] Improper Authorization in Google OAuth Client

## Summary
Severity: High
Advisory: GHSA-f263-c949-w85g
CVE: CVE-2020-7692
CWE: CWE-862, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-09-28
Source: https://github.com/advisories/GHSA-f263-c949-w85g
Type: github-advisory

## Affected
- Maven: `com.google.oauth-client:google-oauth-client` — affected >=0 <1.31.0

## Details
PKCE support is not implemented in accordance with the RFC for OAuth 2.0 for Native Apps. Without the use of PKCE, the authorization code returned by an authorization server is not enough to guarantee that the client that issued the initial authorization request is the one that will be authorized. An attacker is able to obtain the authorization code using a malicious app on the client-side and use it to gain authorization to the protected resource. This affects the package com.google.oauth-client:google-oauth-client before 1.31.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7692
- https://github.com/googleapis/google-oauth-java-client/issues/469
- https://github.com/googleapis/google-oauth-java-client/commit/13433cd7dd06267fc261f0b1d4764f8e3432c824
- https://github.com/googleapis/google-oauth-java-client
- https://lists.apache.org/thread.html/r3db6ac73e0558d64f0b664f2fa4ef0a865e57c5de20f8321d3b48678@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/reae8909b264d1103f321b9ce1623c10c1ddc77dba9790247f2c0c90f@%3Ccommits.druid.apache.org%3E
- https://snyk.io/vuln/SNYK-JAVA-COMGOOGLEOAUTHCLIENT-575276
- https://tools.ietf.org/html/rfc7636%23section-1
- https://tools.ietf.org/html/rfc8252%23section-8.1
