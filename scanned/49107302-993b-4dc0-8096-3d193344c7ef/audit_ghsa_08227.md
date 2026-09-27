# [H] eduMFA Passkeys: missing expiration flag may allow replay attacks and reuse of old challenges 

## Summary
Severity: High
Advisory: GHSA-j5rm-v3vh-vx94
CWE: CWE-287, CWE-613
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-j5rm-v3vh-vx94
Type: github-advisory

## Affected
- PyPI: `edumfa` — affected >=0 <2.9.1

## Details
### Impact
In eduMFA < 2.9.1 userless Passkey/WebAuthn challenges might be replayed and do not expire

### Patches
Fixed in eduMFA >= 2.9.1 by adding validity information to the userless challenges.

### Workarounds
No known workarounds besides disabling userless login altogether.

## References
- https://github.com/eduMFA/eduMFA/security/advisories/GHSA-j5rm-v3vh-vx94
- https://github.com/eduMFA/eduMFA
