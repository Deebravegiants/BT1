# [M] OpenClaw's Nextcloud Talk webhook missing rate limiting on shared secret authentication

## Summary
Severity: Medium
Advisory: GHSA-9528-x887-j2fp
CVE: CVE-2026-33580
CWE: CWE-307
Ecosystem: npm
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-9528-x887-j2fp
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Nextcloud Talk webhook signature failures were not throttled even though the integration relies on an operator-configured shared secret that may be weak.

## Impact

An attacker who could reach the webhook endpoint could brute-force weak secrets online and then forge inbound webhook events.

## Affected Component

`extensions/nextcloud-talk/src/monitor.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `e403decb6e` (`nextcloud-talk: throttle repeated webhook auth failures`).

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9528-x887-j2fp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33580
- https://github.com/openclaw/openclaw/commit/e403decb6e20091b5402780a7ccd2085f98aa3cd
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.28
- https://www.vulncheck.com/advisories/openclaw-brute-force-attack-via-missing-rate-limiting-on-webhook-shared-secret-authentication
