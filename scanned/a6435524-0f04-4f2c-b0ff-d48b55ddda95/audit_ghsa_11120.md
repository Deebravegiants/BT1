# [H] OpenClaw: CLI Remote Onboarding Persists Unauthenticated Discovery Endpoint and Exfiltrates Gateway Credentials

## Summary
Severity: High
Advisory: GHSA-3cw3-5vxw-g2h3
CVE: CVE-2026-41342
CWE: CWE-287, CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-3cw3-5vxw-g2h3
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.28

## Details
## Summary

Remote onboarding accepted discovered gateway endpoints without an explicit trust confirmation before persisting the remote URL and connection details.

## Impact

A malicious or spoofed discovery endpoint could steer onboarding toward an attacker-controlled gateway and capture future gateway credentials or traffic.

## Affected Component

`src/commands/onboard-remote.ts`

## Fixed Versions

- Affected: `<= 2026.3.24`
- Patched: `>= 2026.3.28`
- Latest stable `2026.3.28` contains the fix.

## Fix

Fixed by commit `d6affb17d8` (`CLI: confirm discovered remote gateways before saving config`).

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-3cw3-5vxw-g2h3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41342
- https://github.com/openclaw/openclaw/commit/d6affb17d85f5f5ab08ef9f2b994b257af12e75a
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-unauthenticated-discovery-endpoint-credential-exfiltration-via-remote-onboarding
