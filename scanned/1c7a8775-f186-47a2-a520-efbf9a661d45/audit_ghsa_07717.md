# [M] OpenClaw MS Teams inbound attachment downloader leaks bearer tokens to allowlisted suffix domains

## Summary
Severity: Medium
Advisory: GHSA-7vwx-582j-j332
CVE: CVE-2026-28481
CWE: CWE-201
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-7vwx-582j-j332
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.1

## Details
## Summary

NOTE: This only affects deployments that enable the optional MS Teams extension (Teams channel). If you do not use MS Teams, you are not impacted.

When OpenClaw downloads inbound MS Teams attachments / inline images, it may retry a URL with an `Authorization: Bearer <token>` header after receiving `401` or `403`.

Because the default download allowlist uses suffix matching (and includes some multi-tenant suffix domains), a message that references an untrusted but allowlisted host could cause that bearer token to be sent to the wrong place.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Vulnerable: `<= 2026.1.30`
- Patched: `>= 2026.2.1`

## Fix

- Fix commit: `41cc5bcd4f1d434ad1bbdfa55b56f25025ecbf6b`
- Upgrade to `openclaw >= 2026.2.1`

## Workarounds

- If you do not need MS Teams, disable the MS Teams extension.
- If you must stay on an older version, ensure the auth host allowlist is strict (only Microsoft-owned endpoints that require auth) and avoid wildcard or broad suffix entries.

## Credits

Thanks @yueyueL for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7vwx-582j-j332
- https://nvd.nist.gov/vuln/detail/CVE-2026-28481
- https://github.com/openclaw/openclaw/commit/41cc5bcd4f1d434ad1bbdfa55b56f25025ecbf6b
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.1
- https://www.vulncheck.com/advisories/openclaw-bearer-token-leakage-via-ms-teams-attachment-downloader-suffix-matching
