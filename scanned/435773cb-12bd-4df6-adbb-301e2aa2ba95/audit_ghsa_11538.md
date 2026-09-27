# [H] OpenClaw's incomplete host env sanitization blocklist allows supply-chain redirection via package-manager env overrides

## Summary
Severity: High
Advisory: GHSA-j7p2-qcwm-94v4
CVE: CVE-2026-41387
CWE: CWE-183
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-j7p2-qcwm-94v4
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.22

## Details
## Summary

Host exec env override sanitization did not fail closed for several package-manager and related redirect variables that can steer dependency fetches or startup behavior.

## Impact

An approved exec request could silently redirect package resolution or runtime bootstrap to attacker-controlled infrastructure and execute trojanized content.

## Affected Component

`src/infra/host-env-security-policy.json, src/infra/host-env-security.ts`

## Fixed Versions

- Affected: `< 2026.3.22`
- Patched: `>= 2026.3.22`

## Fix

Fixed by commit `7abfff756d` (`Exec: harden host env override handling across gateway and node`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-j7p2-qcwm-94v4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41387
- https://github.com/openclaw/openclaw/commit/7abfff756d6c68d17e21d1657bbacbaec86de232
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.3.22
- https://www.vulncheck.com/advisories/openclaw-supply-chain-redirection-via-incomplete-host-environment-sanitization
