# [M] OpenClaw: Tlon cite expansion happens before channel and DM authorization is complete

## Summary
Severity: Medium
Advisory: GHSA-vfg3-pqpq-93m4
CVE: CVE-2026-35637
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-vfg3-pqpq-93m4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary
Tlon cite expansion happened before channel and DM authorization completed, allowing cite work and content handling before the final auth decision.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: < 2026.3.22
- Fixed: >= 2026.3.22
- Latest released tag checked: `v2026.3.23-2` (`630f1479c44f78484dfa21bb407cbe6f171dac87`)
- Latest published npm version checked: `2026.3.23-2`

## Fix Commit(s)
- `3cbf932413e41d1836cb91aed1541a28a3122f93`
- `ebee4e2210e1f282a982c7ef2ad79d77a572fc87`

## Release Status
The fix shipped in `v2026.3.22` and remains present in `v2026.3.23` and `v2026.3.23-2`.

## Code-Level Confirmation
- extensions/tlon/src/monitor/index.ts now defers cite expansion until after authorization and preserves explicit empty-allowlist semantics.
- extensions/tlon/src/monitor/utils.ts and extensions/tlon/src/security.test.ts ship the deferred cite expansion behavior and regressions.

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-vfg3-pqpq-93m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-35637
- https://github.com/openclaw/openclaw/commit/3cbf932413e41d1836cb91aed1541a28a3122f93
- https://github.com/openclaw/openclaw/commit/630f1479c44f78484dfa21bb407cbe6f171dac87
- https://github.com/openclaw/openclaw/commit/ebee4e2210e1f282a982c7ef2ad79d77a572fc87
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-premature-cite-expansion-before-authorization-in-channel-and-dm
