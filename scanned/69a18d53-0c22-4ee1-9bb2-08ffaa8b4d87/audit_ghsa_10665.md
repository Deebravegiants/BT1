# [M] OpenClaw: Google Chat and Zalouser group sender allowlist bypass via policy downgrade

## Summary
Severity: Medium
Advisory: GHSA-63mg-xp9j-jfcm
CVE: CVE-2026-33578
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-63mg-xp9j-jfcm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

When only a route-level group allowlist was configured, sender policy resolution silently downgraded from `allowlist` to `open` instead of preserving the configured group policy.

## Impact

Any member of an allowlisted Google Chat space or Zalouser group could interact with the bot even when the operator intended sender-level restrictions.

## Affected Component

`extensions/googlechat/src/monitor-access.ts, extensions/zalouser/src/monitor.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `e64a881ae0` (`Channels: preserve routed group policy`).

OpenClaw thanks @AntAISecurityLab for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-63mg-xp9j-jfcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33578
- https://github.com/openclaw/openclaw/commit/e64a881ae0fb8af18e451163f4c2d611d60cc8e4
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sender-policy-allowlist-bypass-via-policy-downgrade-in-google-chat-and-zalouser-extensions
