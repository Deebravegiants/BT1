# [M] OpenClaw skills.status could leak secrets to operator.read clients

## Summary
Severity: Medium
Advisory: GHSA-8mh7-phf8-xgfm
CVE: CVE-2026-26326
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-8mh7-phf8-xgfm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
### Summary

`skills.status` could disclose secrets to `operator.read` clients by returning raw resolved config values in `configChecks` for skill `requires.config` paths.

### Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected: `<= 2026.2.13`
- Patched: `2026.2.14`

### Details

The gateway method `skills.status` returned a requirements report that included `configChecks[].value` (the resolved value for each `requires.config` entry). If a skill required a broad config subtree (for example `channels.discord`), the report could include secrets such as Discord bot tokens.

`skills.status` is callable with `operator.read`, so read-scoped clients could obtain secrets without `operator.admin` / `config.*` access.

### Fix

- Stop including raw resolved config values in requirement checks (return only `{ path, satisfied }`).
- Narrow the Discord skill requirement to the token key.

Fix commit(s):

- d3428053d95eefbe10ecf04f92218ffcba55ae5a
- ebc68861a61067fc37f9298bded3eec9de0ba783

### Mitigation

Rotate any Discord tokens that may have been exposed to read-scoped clients.

Thanks @simecek for reporting.

---

Fix commits d3428053d95eefbe10ecf04f92218ffcba55ae5a and ebc68861a61067fc37f9298bded3eec9de0ba783 confirmed on main and in v2026.2.14. Upgrade to `openclaw >= 2026.2.14`.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8mh7-phf8-xgfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-26326
- https://github.com/openclaw/openclaw/commit/d3428053d95eefbe10ecf04f92218ffcba55ae5a
- https://github.com/openclaw/openclaw/commit/ebc68861a61067fc37f9298bded3eec9de0ba783
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14
