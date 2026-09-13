# [H] OpenClaw: Sandbox media TOCTOU could read files outside sandbox root

## Summary
Severity: High
Advisory: GHSA-7xmq-g46g-f8pv
CWE: CWE-367, CWE-59
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-7xmq-g46g-f8pv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.1

## Details
### Summary
Sandbox media handling had a time-of-check/time-of-use gap: media paths could be validated first and read later through a separate path. A symlink retarget between those steps could cause reads outside `sandboxRoot`.

### Impact
Affected versions could permit host file reads outside the intended sandbox root in media attachment/image flows.

### Fix
Media reads now use consolidated root-scoped, boundary-safe read paths at use time, removing check/use drift across call sites.

### Affected and Patched Versions
- Affected: `<= 2026.2.26`
- Patched: `2026.3.1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-7xmq-g46g-f8pv
- https://github.com/openclaw/openclaw
