# [M] zcap has incomplete expiration checks in capability chains.

## Summary
Severity: Medium
Advisory: GHSA-hp8h-7x69-4wmv
CVE: CVE-2024-31995
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-hp8h-7x69-4wmv
Type: github-advisory

## Affected
- npm: `@digitalbazaar/zcap` — affected >=0 <9.0.1

## Details
### Impact

When invoking a capability with a chain depth of 2, i.e., it is delegated directly from the root capability, the `expires` property is not properly checked against the current date or other `date` param.  This can allow invocations outside of the original intended time period.  A zcap still cannot be invoked without being able to use the associated private key material.

### Patches

`@digitalbazaar/zcap` v9.0.1 fixes expiration checking.

### Workarounds

A zcap could be revoked at any time.

### References

https://github.com/digitalbazaar/zcap/pull/82

## References
- https://github.com/digitalbazaar/zcap/security/advisories/GHSA-hp8h-7x69-4wmv
- https://nvd.nist.gov/vuln/detail/CVE-2024-31995
- https://github.com/digitalbazaar/zcap/pull/82
- https://github.com/digitalbazaar/zcap/commit/261eea040109b6e25159c88d8ed49d3c37f8fcfe
- https://github.com/digitalbazaar/zcap/commit/55f8549c80124b85dfb0f3dcf83f2c63f42532e5
- https://github.com/digitalbazaar/zcap
