# [M] OpenClaw: Google Chat app-url webhook auth accepted non-deployment add-on principals

## Summary
Severity: Medium
Advisory: GHSA-mp66-rf4f-mhh8
CVE: CVE-2026-35622
CWE: CWE-290, CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-mp66-rf4f-mhh8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Google Chat app-url webhook verification accepted add-on principals outside the intended deployment binding.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `a47722de7e3c9cbda8d5512747ca7e3bb8f6ee66`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- extensions/googlechat/src/auth.ts now requires expectedAddOnPrincipal matching for add-on principals and rejects unexpected issuers.
- extensions/googlechat/src/monitor-webhook.ts passes the configured appPrincipal into auth verification for the shipped webhook path.

OpenClaw thanks @ijxpwastaken for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-mp66-rf4f-mhh8
- https://nvd.nist.gov/vuln/detail/CVE-2026-35622
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/a47722de7e3c9cbda8d5512747ca7e3bb8f6ee66
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-improper-authentication-verification-in-google-chat-webhook
