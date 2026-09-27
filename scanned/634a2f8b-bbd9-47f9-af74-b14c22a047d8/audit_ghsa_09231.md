# [M] eduMFA: Unauthenticated Failcounter Increment on Resolver Tokens via /validate/check

## Summary
Severity: Medium
Advisory: GHSA-74r7-3mjm-jc5v
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-74r7-3mjm-jc5v
Type: github-advisory

## Affected
- PyPI: `edumfa` — affected >=0 <2.9.1

## Details
### Impact
If the resolver parameter is passed, but the user does not exist, all failcounters of tokens in that resolver will be increased.

### Patches
This, along with other issues, was fixed in eduMFA v2.9.1.

### Workarounds
Limiting access to `/validate/check` to client applications (i.e. Shibboleth/FreeRADIUS) using an authorization policy with `api_key_required` or using e.g. the reverse proxy.

## References
- https://github.com/eduMFA/eduMFA/security/advisories/GHSA-74r7-3mjm-jc5v
- https://github.com/eduMFA/eduMFA
