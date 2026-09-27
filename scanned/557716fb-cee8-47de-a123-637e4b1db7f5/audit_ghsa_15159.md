# [H] CIRCL's Kyber: timing side-channel (kyberslash2)

## Summary
Severity: High
Advisory: GHSA-9763-4f94-gfch
Ecosystem: Go
Published: 2024-01-08
Source: https://github.com/advisories/GHSA-9763-4f94-gfch
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/circl` — affected >=0 <1.3.7

## Details
### Impact
On some platforms, when an attacker can time decapsulation of Kyber on forged cipher texts, they could possibly learn (parts of) the secret key.

Does not apply to ephemeral usage, such as when used in the regular way in TLS.

### Patches
Patched in 1.3.7.

### References
- [kyberslash.cr.yp.to](https://kyberslash.cr.yp.to/)

## References
- https://github.com/cloudflare/circl/security/advisories/GHSA-9763-4f94-gfch
- https://github.com/cloudflare/circl/commit/75ef91e8a2f438e6ce2b6e620d236add8be1887d
- https://github.com/cloudflare/circl
- https://kyberslash.cr.yp.to
