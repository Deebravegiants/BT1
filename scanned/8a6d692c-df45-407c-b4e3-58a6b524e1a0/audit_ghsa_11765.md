# [H] OpenClaw: Gateway Plugin HTTP Auth Grants Unrestricted operator.admin Runtime Scope to All Callers

## Summary
Severity: High
Advisory: GHSA-qm2m-28pf-hgjw
CVE: CVE-2026-35669
CWE: CWE-266, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-qm2m-28pf-hgjw
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0

## Details
## Summary

Gateway Plugin HTTP auth: "gateway" Mints operator.admin Runtime Scope

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Gateway-authenticated plugin HTTP routes previously created a runtime scope set that included `operator.admin` regardless of caller-granted scopes. Commit `ec2dbcff9afd8a52e00de054b506c91726d9fbbe` keeps plugin HTTP runtime scopes least-privileged and preserves caller scope boundaries.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `ec2dbcff9afd8a52e00de054b506c91726d9fbbe`.

## Fix Commit(s)

- `ec2dbcff9afd8a52e00de054b506c91726d9fbbe`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-qm2m-28pf-hgjw
- https://github.com/openclaw/openclaw/commit/ec2dbcff9afd8a52e00de054b506c91726d9fbbe
- https://github.com/openclaw/openclaw
