# [M] OpenClaw hardened cron webhook delivery against SSRF

## Summary
Severity: Medium
Advisory: GHSA-w45g-5746-x9fp
CVE: CVE-2026-27488
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:N/SI:L/SA:L (CVSS_V4)
Published: 2026-02-20
Source: https://github.com/advisories/GHSA-w45g-5746-x9fp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
## Affected Packages / Versions

- `openclaw` npm package versions `<= 2026.2.17`.

## Vulnerability
Cron webhook delivery in `src/gateway/server-cron.ts` used `fetch()` directly, so webhook targets could reach private/metadata/internal endpoints without SSRF policy checks.

## Fix Commit(s)
- `99db4d13e`
- `35851cdaf`

Thanks @Adam55A-code for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-w45g-5746-x9fp
- https://nvd.nist.gov/vuln/detail/CVE-2026-27488
- https://github.com/openclaw/openclaw/commit/99db4d13e5c139883ef0def9ff963e9273179655
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.19
