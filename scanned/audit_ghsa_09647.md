# [M] OpenClaw: Untrusted workspace channel shadows could execute during built-in channel setup

## Summary
Severity: Medium
Advisory: GHSA-2qrv-rc5x-2g2h
CVE: CVE-2026-41295
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-2qrv-rc5x-2g2h
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, built-in channel setup and login could resolve an untrusted workspace channel shadow before the plugin was explicitly trusted. A malicious workspace plugin that claimed a bundled channel id could execute during channel setup even while still disabled.

## Impact

A cloned workspace could turn channel setup for a built-in channel into unintended in-process code execution from an untrusted workspace plugin. This bypassed the intended workspace-plugin trust boundary during setup and login.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `53c29df2a9eb242a70d0ff29f3d1e67c8d6801f0` — ignore untrusted workspace channel shadows during setup resolution

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-2qrv-rc5x-2g2h
- https://github.com/openclaw/openclaw/commit/53c29df2a9eb242a70d0ff29f3d1e67c8d6801f0
- https://github.com/openclaw/openclaw
