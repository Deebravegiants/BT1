# [H] ZITADEL: Unauthorized Token Privilege Escalation in OAuth2 Token Exchange

## Summary
Severity: High
Advisory: CVE-2026-56668
Aliases: GHSA-vrh8-c9cm-wh8v
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-56668
Type: osv

## Details
ZITADEL is an open source identity management platform. Prior to 4.15.3, ZITADEL's OAuth2 Token Exchange endpoint for urn:ietf:params:oauth:grant-type:token-exchange does not verify that the subject token belongs to the requesting client or that requested scopes remain within the original token's scopes, allowing a low-privilege token to be exchanged for elevated permissions at another application. This issue is fixed in version 4.15.3.

## References
- https://github.com/zitadel/zitadel/releases/tag/v4.15.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56668.json
- https://github.com/zitadel/zitadel/security/advisories/GHSA-vrh8-c9cm-wh8v
- https://nvd.nist.gov/vuln/detail/CVE-2026-56668
- https://github.com/zitadel/zitadel/commit/e2886a61670ca8fd41c9434f87036546e5620bcc
