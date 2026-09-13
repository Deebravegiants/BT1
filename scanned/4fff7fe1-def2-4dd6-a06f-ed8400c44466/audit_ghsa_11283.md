# [H] OpenClaw: `browser.request` let `operator.write` persist admin-only browser profile changes

## Summary
Severity: High
Advisory: GHSA-vmhq-cqm9-6p7q
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-vmhq-cqm9-6p7q
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.11

## Details
### Summary

An authorization mismatch in the gateway let an authenticated caller with only `operator.write` use `browser.request` to reach browser profile management routes that persist configuration to disk. In practice, this exposed an admin-only configuration write primitive through `/profiles/create`.

### Impact

A write-scoped operator could create or modify browser profiles and store attacker-chosen remote CDP endpoints without holding `operator.admin`.

### Affected versions

`openclaw` `<= 2026.3.8`

### Patch

Fixed in `openclaw` `2026.3.11` and included in later releases such as `2026.3.12`. Browser profile creation now requires the correct admin boundary, and regression tests cover the write-vs-admin authorization split.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vmhq-cqm9-6p7q
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.11
