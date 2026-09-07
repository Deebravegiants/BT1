# [M] OpenClaw: QQBot direct media upload skipped URL SSRF validation

## Summary
Severity: Medium
Advisory: GHSA-c4qg-j8jg-42q5
CVE: CVE-2026-44117
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-c4qg-j8jg-42q5
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.20

## Details
## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `< 2026.4.20`
- Patched version: `2026.4.20`

## Impact

The QQBot direct-upload media path could forward attacker-controlled image URLs without applying the SSRF validation used by the local download path. This could make configured QQBot media delivery request or relay URLs the operator did not intend to allow.

The affected path is limited to QQBot outbound media handling and does not expose arbitrary local files. Severity is low.

## Fix

OpenClaw now validates QQBot direct-upload media URLs before `uploadC2CMedia` and `uploadGroupMedia` direct-upload calls.

Fix commit:

- `49db424c8001f2f419aad85f434894d8d85c1a09`

## Release

Fixed in OpenClaw `2026.4.20`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-c4qg-j8jg-42q5
- https://nvd.nist.gov/vuln/detail/CVE-2026-44117
- https://github.com/openclaw/openclaw/commit/49db424c8001f2f419aad85f434894d8d85c1a09
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-server-side-request-forgery-in-qqbot-direct-media-upload
