# [M] OpenClaw: Unicode canonicalization drift in node metadata policy classification could broaden node allowlists

## Summary
Severity: Medium
Advisory: GHSA-392f-ggf5-fp3c
CWE: CWE-176, CWE-436
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-392f-ggf5-fp3c
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.3.1

## Details
### Summary
A paired node could supply Unicode-confusable `platform` or `deviceFamily` metadata that passed metadata pinning but classified differently for command policy resolution, broadening default node command allowlists.

### Impact
This is a policy-bypass issue within the paired-node trust boundary and can expand node command availability beyond intended defaults.

### Fix
Node metadata canonicalization was hardened against confusables, and unknown platform defaults were made conservative (excluding `system.run` and `system.which` unless explicitly allowlisted).

### Affected and Patched Versions
- Affected: `<= 2026.2.26`
- Patched: `2026.3.1`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-392f-ggf5-fp3c
- https://github.com/openclaw/openclaw
