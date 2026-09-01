# [H] LND Onion Bomb

## Summary
Severity: High
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
CVE: CVE-2024-38359
CWE: Improper Input Validation
Published: 2024-06-20
Source: https://github.com/lightningnetwork/lnd/security/advisories/GHSA-9gxx-58q6-42p7
Type: github-advisory

## Details
### Impact

A parsing vulnerability in lnd's onion processing logic led to a DoS vector due to excessive memory allocation. 

### Patches

The issue was patched in lnd [v0.17.0](https://github.com/lightningnetwork/lnd/releases/tag/v0.17.0-beta). Users should update to a version >= v0.17.0 to be protected. 

### References

Detailed blog post: https://morehouse.github.io/lightning/lnd-onion-bomb/

Developer discussion: https://delvingbitcoin.org/t/dos-disclosure-lnd-onion-bomb/979
