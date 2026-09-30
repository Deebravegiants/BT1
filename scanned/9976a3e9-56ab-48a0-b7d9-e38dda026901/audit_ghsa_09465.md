# [M] OpenClaw's Webhooks SecretRef route secret remains valid after rotation/reload

## Summary
Severity: Medium
Advisory: GHSA-q8ff-7ffm-m3r9
CVE: CVE-2026-45005
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-q8ff-7ffm-m3r9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.23

## Details
## Summary

OpenClaw webhooks allowed route secrets to be backed by `SecretRef` values, but cached the resolved secret for a route. After an operator rotated the underlying secret and ran `openclaw secrets reload`, the previous resolved webhook secret could remain valid until the plugin or gateway restarted.

## Impact

An attacker who already had a previously valid webhook route secret could continue authenticating webhook requests after the operator rotated the secret and reloaded secrets. This weakened credential rotation for webhook routes and could allow continued invocation of the configured webhook task flow until restart.

## Affected Packages / Versions

- Package: `openclaw` on npm
- Affected: versions before `2026.4.23`
- Fixed: `2026.4.23`
- Latest stable verified fixed: `openclaw@2026.4.23`, tag `v2026.4.23`

## Fix

Webhook route authentication now resolves `SecretRef`-backed route secrets on each request. A rotated secret becomes effective after `openclaw secrets reload` without requiring a gateway or plugin restart, and the old secret is rejected.

## Fix Commit(s)

- `36c4a372a0ad5dca8bfc0d93f7aab9c2f2de66fa` (`fix(webhooks): reload route secrets per request`)

## Severity

Severity remains `medium`. The attack requires possession of a previously valid route secret, but the stale credential can continue to authorize webhook actions after rotation.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-q8ff-7ffm-m3r9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45005
- https://github.com/openclaw/openclaw/commit/36c4a372a0ad5dca8bfc0d93f7aab9c2f2de66fa
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-webhook-route-secret-cache-not-invalidated-after-rotation
