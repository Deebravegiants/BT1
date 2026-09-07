# [H] OpenClaw: Command-authorized non-owners could reach owner-only `/config` and `/debug` surfaces

## Summary
Severity: High
Advisory: GHSA-r7vr-gr74-94p8
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-r7vr-gr74-94p8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.12

## Details
### Summary

OpenClaw documented `/config` and `/debug` as owner-only commands, but the command handlers checked only whether the sender was command-authorized. A lower-trust sender who was intentionally allowed to run commands could still reach privileged configuration and debugging surfaces.

### Impact

This allowed a non-owner sender to read or change privileged configuration that should have remained restricted to owners.

### Affected versions

`openclaw` `<= 2026.3.11`

### Patch

Fixed in `openclaw` `2026.3.12`. Owner checks are now enforced for privileged command surfaces, and regression tests cover `/config` and `/debug` access control.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-r7vr-gr74-94p8
- https://github.com/openclaw/openclaw/pull/44305
- https://github.com/openclaw/openclaw/commit/08aa57a3de37d337b226ae861f573779f112ff2e
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.12
