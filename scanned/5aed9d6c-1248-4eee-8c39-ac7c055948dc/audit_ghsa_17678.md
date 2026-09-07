# [C] rfc3161-client has insufficient verification for timestamp response signatures

## Summary
Severity: Critical
Advisory: GHSA-6qhv-4h7r-2g9m
CVE: CVE-2025-52556
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-20
Source: https://github.com/advisories/GHSA-6qhv-4h7r-2g9m
Type: github-advisory

## Affected
- PyPI: `rfc3161-client` — affected >=0 <1.0.3

## Details
### Impact

`rfc3161-client` 1.0.2 and earlier contain a flaw in their timestamp response signature verification logic. In particular, it performs chain verification against the TSR's embedded certificates up to the trusted root(s), but fails to verify the TSR's own signature against the timestamping leaf certificates. Consequently, vulnerable versions perform insufficient signature validation to properly consider a TSR verified, as the attacker can introduce _any_ TSR signature so long as the embedded leaf chains up to some root TSA.

### Patches

Users should immediately upgrade to `rfc3161-client` 1.0.3 or later.

### Workarounds

There is no workaround possible. Users should immediately upgrade to a fixed version.

## References
- https://github.com/trailofbits/rfc3161-client/security/advisories/GHSA-6qhv-4h7r-2g9m
- https://nvd.nist.gov/vuln/detail/CVE-2025-52556
- https://github.com/trailofbits/rfc3161-client/commit/724a184f953e3f171f85cb223871172b41b0d0dc
- https://github.com/trailofbits/rfc3161-client
