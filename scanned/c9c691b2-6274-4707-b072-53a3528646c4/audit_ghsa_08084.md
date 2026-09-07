# [M] OpenClaw hardened the skill download target directory validation

## Summary
Severity: Medium
Advisory: GHSA-h7f7-89mm-pqh6
CVE: CVE-2026-27008
CWE: CWE-73
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-h7f7-89mm-pqh6
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.15

## Details
## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected versions: `<= 2026.2.14`
- Fixed in: planned release `2026.2.15`

## Impact
A bug in `download` skill installation allowed `targetDir` values from skill frontmatter to resolve outside the per-skill tools directory if not strictly validated.
In the admin-only `skills.install` flow, this could write files outside the intended install sandbox.

## Fix Commit(s)
- 2363e1b08 fix(security): restrict skill download target paths
- b6305e972 test(skills): split installer security coverage

## Acknowledgement
Thanks @Adam55A-code for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h7f7-89mm-pqh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27008
- https://github.com/openclaw/openclaw/commit/2363e1b0853a028e47f90dcc1066e3e9809d65f1
- https://github.com/openclaw/openclaw/commit/b6305e97256d67e439719faacf5af3de9727d6e1
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.15
