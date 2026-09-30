# [H] Lightning Network Daemon (LND)'s onion processing logic leads to a denial of service

## Summary
Severity: High
Advisory: GHSA-9gxx-58q6-42p7
CVE: CVE-2024-38359
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-20
Source: https://github.com/advisories/GHSA-9gxx-58q6-42p7
Type: github-advisory

## Affected
- Go: `github.com/lightningnetwork/lnd` — affected >=0 <0.17.0-beta

## Details
### Impact

A parsing vulnerability in lnd's onion processing logic led to a DoS vector due to excessive memory allocation.  

### Patches

The issue was patched in lnd [v0.17.0](https://github.com/lightningnetwork/lnd/releases/tag/v0.17.0-beta). Users should update to a version >= v0.17.0 to be protected. 

### References

Detailed blog post: https://morehouse.github.io/lightning/lnd-onion-bomb/

Developer discussion: https://delvingbitcoin.org/t/dos-disclosure-lnd-onion-bomb/979

## References
- https://github.com/lightningnetwork/lnd/security/advisories/GHSA-9gxx-58q6-42p7
- https://nvd.nist.gov/vuln/detail/CVE-2024-38359
- https://delvingbitcoin.org/t/dos-disclosure-lnd-onion-bomb/979
- https://github.com/lightningnetwork/lnd
- https://github.com/lightningnetwork/lnd/releases/tag/v0.17.0-beta
- https://lightning.network
- https://morehouse.github.io/lightning/lnd-onion-bomb
