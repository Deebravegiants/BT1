# [M] OpenClaw's complex interpreter pipelines could skip exec script preflight validation

## Summary
Severity: Medium
Advisory: GHSA-fvx6-pj3r-5q4q
CVE: CVE-2026-34425
CWE: CWE-184
Ecosystem: npm
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-fvx6-pj3r-5q4q
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.4.2

## Details
## Summary

Before OpenClaw 2026.4.2, exec script preflight validation could fail open on complex interpreter invocations such as pipes or other non-simple command forms. In those cases, script-content validation could be skipped entirely.

## Impact

An attacker-controlled command shape could bypass the intended preflight validation for script execution. This weakened a defense-in-depth guard that was meant to block unsafe script content before execution.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected versions: `<= 2026.4.1`
- Patched versions: `>= 2026.4.2`
- Latest published npm version: `2026.4.1`

## Fix Commit(s)

- `8aceaf5d0f0ec552b75a792f7f0a3bfa5b091513` — close the fail-open bypass in exec script preflight

## Release Process Note

The fix is present on `main` and is staged for OpenClaw `2026.4.2`. Publish this advisory after the `2026.4.2` npm release is live.

Thanks @iskindar for reporting, and thanks @wsparks-vc for coordination.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fvx6-pj3r-5q4q
- https://nvd.nist.gov/vuln/detail/CVE-2026-34425
- https://github.com/openclaw/openclaw/commit/8aceaf5d0f0ec552b75a792f7f0a3bfa5b091513
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-shell-bleed-protection-preflight-validation-bypass
