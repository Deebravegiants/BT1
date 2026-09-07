# [M] OpenClaw: Zalo replay dedupe keys could suppress messages across chats or senders

## Summary
Severity: Medium
Advisory: GHSA-rxmx-g7hr-8mx4
CVE: CVE-2026-41354
CWE: CWE-349, CWE-440
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-rxmx-g7hr-8mx4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, Zalo webhook replay dedupe keys were not scoped strongly enough across chat and sender dimensions. Legitimate events from different conversations or senders could collide and be dropped as duplicates.

## Impact

Cross-conversation or cross-sender collisions could cause silent message suppression and break bot workflows. This was an availability issue in webhook event processing.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `ef7c553dd16ee579f1d1a363f5881a99726c1412` — scope Zalo webhook replay dedupe across the missing event dimensions

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @D0ub1e-D for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rxmx-g7hr-8mx4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41354
- https://github.com/openclaw/openclaw/commit/ef7c553dd16ee579f1d1a363f5881a99726c1412
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-insufficient-scope-in-zalo-webhook-replay-dedupe-keys
