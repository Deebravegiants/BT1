# [M] OpenClaw validates Zalo outbound photo URLs through the SSRF guard

## Summary
Severity: Medium
Advisory: GHSA-2hh7-c75g-qj2r
CVE: CVE-2026-44116
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-2hh7-c75g-qj2r
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.22

## Details
## Summary
Zalo outbound photo URLs are validated through the SSRF guard.

## Affected Packages / Versions
- Package: openclaw (npm)
- Affected versions: <= 2026.4.21
- Fixed version: 2026.4.22

## Impact
The Zalo plugin could forward an attacker-controlled outbound photo URL to the Zalo Bot API without first applying OpenClaw's SSRF validation policy.

## Fix
Zalo sendPhoto now parses and validates outbound photo URLs with the shared SSRF hostname policy before posting to Zalo, and media-reply paths route through the guarded outbound media helpers.

## Fix Commit(s)
- a65eb1b864b7630c1242a82de9e5799b80583c3f

## Verification
- The fix commit is contained in the public v2026.4.22 tag.
- openclaw@2026.4.22 is published on npm and the compiled package contains the fix.
- Focused regression coverage for this path passed before publication.

OpenClaw thanks @foodlook for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2hh7-c75g-qj2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-44116
- https://github.com/openclaw/openclaw/commit/a65eb1b864b7630c1242a82de9e5799b80583c3f
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-server-side-request-forgery-in-zalo-photo-url-validation
