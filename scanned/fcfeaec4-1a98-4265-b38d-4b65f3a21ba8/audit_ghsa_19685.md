# [H] In Azle, calling `setTimer` causes infinite loop of timers

## Summary
Severity: High
Advisory: GHSA-xc76-5pf9-mx8m
CVE: CVE-2025-29776
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2025-03-14
Source: https://github.com/advisories/GHSA-xc76-5pf9-mx8m
Type: github-advisory

## Affected
- npm: `azle` — affected >=0.27.0 <0.30.0

## Details
### Impact

Calling `setTimer` in Azle versions `0.27.0`, `0.28.0`, and `0.29.0` causes an immediate infinite loop of timers to be executed on the canister, each timer attempting to clean up the global state of the previous timer.

The infinite loop will occur with any valid invocation of `setTimer`.

### Patches

The problem has been fixed as of Azle version `0.30.0`.

### Workarounds

If a canister is caught in this infinite loop after calling `setTimer`, the canister can be upgraded and the timers will all be cleared, thus ending the loop.

## References
- https://github.com/demergent-labs/azle/security/advisories/GHSA-xc76-5pf9-mx8m
- https://nvd.nist.gov/vuln/detail/CVE-2025-29776
- https://github.com/demergent-labs/azle
- https://github.com/demergent-labs/azle/releases/tag/0.30.0
