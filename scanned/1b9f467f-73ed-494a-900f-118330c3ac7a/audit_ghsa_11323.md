# [C] OpenClaw: Silent privilege escalation via gateway shared-auth reconnect

## Summary
Severity: Critical
Advisory: GHSA-fqw4-mph7-2vr8
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:A/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-fqw4-mph7-2vr8
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0

## Details
## Summary

Gateway local shared-auth reconnect silently widens paired device scope from operator.read to operator.admin and reach node RCE

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Silent local shared-auth reconnects could previously auto-approve `scope-upgrade` requests and widen a paired device from `operator.read` to `operator.admin`. Commit `81ebc7e0344fd19c85778e883bad45e2da972229` blocks silent reconnect scope upgrades so widened scopes require an explicit pairing approval instead of an implicit local reconnect path.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `81ebc7e0344fd19c85778e883bad45e2da972229`.

## Fix Commit(s)

- `81ebc7e0344fd19c85778e883bad45e2da972229`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fqw4-mph7-2vr8
- https://github.com/openclaw/openclaw/commit/81ebc7e0344fd19c85778e883bad45e2da972229
- https://github.com/openclaw/openclaw
