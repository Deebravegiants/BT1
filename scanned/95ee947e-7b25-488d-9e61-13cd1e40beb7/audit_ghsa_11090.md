# [M] OpenClaw affected by iMessage remote attachment SCP hardening (strict host-key checks and remoteHost validation)

## Summary
Severity: Medium
Advisory: GHSA-2mc2-g238-722j
CWE: CWE-295, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-2mc2-g238-722j
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
## Summary

Remote iMessage attachment fetches used SCP with trust-on-first-use host-key behavior and accepted unvalidated remote host tokens.

Before the fix:
- SCP used `StrictHostKeyChecking=accept-new` in the remote attachment path.
- `channels.imessage.remoteHost` was not validated as a strict SSH host token.

## Impact

In remote iMessage deployments that use SCP attachment fetching, a first-connection MITM/DNS-poisoning scenario could cause the wrong host key to be trusted. Unsafe remote host token values could also alter SCP argument semantics.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Latest published npm version currently affected: `2026.2.17`
- Vulnerable range (structured field): `<= 2026.2.17`
- Patched version (pre-set for next release): `>= 2026.2.19`

## Fix

The fix hardens remote attachment SSH/SCP handling by:
- requiring `StrictHostKeyChecking=yes` for SCP and SSH tunnel paths,
- adding strict `remoteHost` normalization/validation,
- adding `--` argument barrier for SCP remote source parsing,
- validating `channels.imessage.remoteHost` in config schema,
- rejecting unsafe auto-detected host tokens at runtime.

## Fix Commit(s)

- Pushed to `main`: 49d0def6d1e88f002026b1d2a35aa615d48a751a

OpenClaw thanks @allsmog for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2mc2-g238-722j
- https://github.com/openclaw/openclaw/commit/49d0def6d1e88f002026b1d2a35aa615d48a751a
- https://github.com/openclaw/openclaw
