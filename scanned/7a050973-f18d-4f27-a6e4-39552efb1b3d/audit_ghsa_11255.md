# [M] OpenClaw has an opt-in insecure Control UI auth over plaintext HTTP could allow privileged access

## Summary
Severity: Medium
Advisory: GHSA-3cvx-236h-m9fj
CVE: CVE-2026-32034
CWE: CWE-285, CWE-319, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-3cvx-236h-m9fj
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.21

## Details
## Description

In affected releases, when an operator explicitly enabled `gateway.controlUi.allowInsecureAuth: true` and exposed the gateway over plaintext HTTP, Control UI authentication could permit privileged operator access without the intended device identity + pairing guarantees.

This required an insecure deployment choice and credential exposure risk (for example, plaintext transit or prior token leak). It was fixed on `main` in commit `40a292619e1f2be3a3b1db663d7494c9c2dc0abf` ([PR #20684](https://github.com/openclaw/openclaw/pull/20684)).

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Affected published versions: `<= 2026.2.19-2`
- Planned patched version: `2026.2.21`

## Impact

In these explicitly insecure deployments, an attacker with leaked/intercepted credentials could obtain high-privilege Control UI access.

## Fix Commit(s)

- `40a292619e1f2be3a3b1db663d7494c9c2dc0abf` (merged 2026-02-20)

OpenClaw thanks @Vasco0x4 for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3cvx-236h-m9fj
- https://nvd.nist.gov/vuln/detail/CVE-2026-32034
- https://github.com/openclaw/openclaw/pull/20684
- https://github.com/openclaw/openclaw/commit/40a292619e1f2be3a3b1db663d7494c9c2dc0abf
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-insecure-control-ui-authentication-over-plaintext-http
