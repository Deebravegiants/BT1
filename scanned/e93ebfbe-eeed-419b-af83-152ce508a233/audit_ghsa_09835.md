# [H] OpenClaw: Incomplete host-env-security-policy allows untrusted model to substitute compiler binaries via env overrides

## Summary
Severity: High
Advisory: GHSA-g8xp-qx39-9jq9
CVE: CVE-2026-41373
CWE: CWE-427
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-g8xp-qx39-9jq9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.31

## Details
## Summary
Incomplete `host-env-security-policy.json` allows untrusted model to substitute compiler binaries (`CC`, `CXX`, `CARGO_BUILD_RUSTC`, `CMAKE_C_COMPILER`) via env overrides on approved host exec requests

## Current Maintainer Triage
- Status: narrow
- Normalized severity: medium
- Assessment: Shipped v2026.3.28 host-env policy missed compiler override vars, but exploitation still requires an approved host-exec request inside the existing exec trust domain, so medium not high.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version: `2026.3.31`
- Vulnerable version range: `<=2026.3.28`
- Patched versions: `>= 2026.3.31`
- First stable tag containing the fix: `v2026.3.31`

## Fix Commit(s)
- `e277a37f896b5011a1df06e6490c6630074d0afa` — 2026-03-30T20:06:32+01:00

OpenClaw thanks @tdjackey for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-g8xp-qx39-9jq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-41373
- https://github.com/openclaw/openclaw/commit/e277a37f896b5011a1df06e6490c6630074d0afa
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.31
- https://www.vulncheck.com/advisories/openclaw-compiler-binary-substitution-via-environment-variable-override-in-host-execution-policy
