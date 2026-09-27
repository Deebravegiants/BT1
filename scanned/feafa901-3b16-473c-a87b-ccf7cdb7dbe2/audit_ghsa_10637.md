# [M] OpenClaw: Windows-compatible env override keys could bypass system.run approval binding

## Summary
Severity: Medium
Advisory: GHSA-98ch-45wp-ch47
CWE: CWE-178
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-98ch-45wp-ch47
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, system-run approval binding normalized environment override keys differently from host execution. Windows-compatible keys could be omitted from the approval binding while still being injected at execution time.

## Impact

An approved command could run with attacker-chosen environment overrides that were not represented in the approval binding. This created an approval-integrity gap for affected host-exec flows.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `7eb094a00d80e9f6bf0e62f2c45d3b88ff67c04d` — align approval binding with execution-time env-key normalization

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @iskindar for reporting, and thanks @wsparks-vc for coordination.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-98ch-45wp-ch47
- https://github.com/openclaw/openclaw/commit/7eb094a00d80e9f6bf0e62f2c45d3b88ff67c04d
- https://github.com/openclaw/openclaw
