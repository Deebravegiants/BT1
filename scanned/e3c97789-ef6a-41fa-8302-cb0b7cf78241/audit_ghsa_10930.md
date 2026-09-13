# [H] OpenClaw has non-constant-time token comparison in hooks authentication

## Summary
Severity: High
Advisory: GHSA-jmm5-fvh5-gf4p
CVE: CVE-2026-28464
CWE: CWE-208
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-jmm5-fvh5-gf4p
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.12

## Details
## Summary

OpenClaw hooks previously compared the provided hook token using a regular string comparison. Because this comparison is not constant-time, an attacker with network access to the hooks endpoint could potentially use timing measurements across many requests to gradually infer the token.

In practice, this typically requires hooks to be exposed to an untrusted network and a large number of requests; real-world latency and jitter can make reliable measurement difficult.

## Affected Packages / Versions

- openclaw (npm): < 2026.2.12

## Patched Versions

- openclaw (npm): >= 2026.2.12

## Mitigations

- Upgrade to openclaw >= 2026.2.12.
- If users cannot upgrade immediately: restrict network access to the hooks endpoint and rotate the hooks token after updating.

## Fix Commit(s)

- 113ebfd6a23c4beb8a575d48f7482593254506ec

OpenClaw thanks @akhmittra for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-jmm5-fvh5-gf4p
- https://nvd.nist.gov/vuln/detail/CVE-2026-28464
- https://github.com/openclaw/openclaw/commit/113ebfd6a23c4beb8a575d48f7482593254506ec
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-timing-attack-in-hooks-token-authentication
