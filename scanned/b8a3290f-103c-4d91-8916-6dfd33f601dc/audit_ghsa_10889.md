# [C] OpenClaw: Gateway Backend Reconnect lets Non-Admin Operator Scopes Self-Claim operator.admin

## Summary
Severity: Critical
Advisory: GHSA-9hjh-fr4f-gxc4
CVE: CVE-2026-35663
CWE: CWE-269, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-9hjh-fr4f-gxc4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0

## Details
## Summary

Gateway Backend Reconnect lets Non-Admin Operator Scopes Self-Claim operator.admin

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Backend-labeled reconnects could previously self-request broader scopes and bypass pairing, allowing non-admin operators to reconnect as `operator.admin`. Commit `d3d8e316bd819d3c7e34253aeb7eccb2510f5f48` removes the backend self-pairing skip and requires pairing when requested scopes exceed the approved baseline.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `d3d8e316bd819d3c7e34253aeb7eccb2510f5f48`.

## Fix Commit(s)

- `d3d8e316bd819d3c7e34253aeb7eccb2510f5f48`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9hjh-fr4f-gxc4
- https://github.com/openclaw/openclaw/commit/d3d8e316bd819d3c7e34253aeb7eccb2510f5f48
- https://github.com/openclaw/openclaw
