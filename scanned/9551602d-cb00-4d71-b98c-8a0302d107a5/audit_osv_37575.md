# [C] OpenOLAT: Authentication bypass via forged JWT in OIDC implicit flow

## Summary
Severity: Critical
Advisory: CVE-2026-31946
Aliases: GHSA-v8vp-x4q4-2vch
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-31946
Type: osv

## Details
OpenOlat is an open source web-based e-learning platform for teaching, learning, assessment and communication. From version 10.5.4 to before version 20.2.5, OpenOLAT's OpenID Connect implicit flow implementation does not verify JWT signatures. The JSONWebToken.parse() method silently discards the signature segment of the compact JWT (header.payload.signature), and the getAccessToken() methods in both OpenIdConnectApi and OpenIdConnectFullConfigurableApi only validate claim-level fields (issuer, audience, state, nonce) without any cryptographic signature verification against the Identity Provider's JWKS endpoint. This issue has been patched in version 20.2.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31946.json
- https://github.com/OpenOLAT/OpenOLAT/security/advisories/GHSA-v8vp-x4q4-2vch
- https://nvd.nist.gov/vuln/detail/CVE-2026-31946
