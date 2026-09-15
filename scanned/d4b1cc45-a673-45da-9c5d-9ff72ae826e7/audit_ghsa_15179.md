# [H] safe_pqc_kyber leaks parts of secret keys

## Summary
Severity: High
Advisory: GHSA-p4v8-jgcv-9g75
Ecosystem: crates.io
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-p4v8-jgcv-9g75
Type: github-advisory

## Affected
- crates.io: `safe_pqc_kyber` — affected >=0 <0.6.2

## Details
### Impact
On some platforms, when an attacker can time decapsulation, and in particular when the attacker can forge cipher texts, they can learn (parts of) the secret key.

Does not apply to ephemeral usage, such as when used in the regular way in TLS.

### Patches
Patched in 0.6.2.


### References
- [kyberslash.cr.yp.to](https://kyberslash.cr.yp.to)

## References
- https://github.com/bwesterb/argyle-kyber/security/advisories/GHSA-p4v8-jgcv-9g75
- https://github.com/bwesterb/argyle-kyber/commit/b5c6ad13f4eece80e59c6ebeafd787ba1519f5f6
- https://github.com/bwesterb/argyle-kyber
- https://kyberslash.cr.yp.to
