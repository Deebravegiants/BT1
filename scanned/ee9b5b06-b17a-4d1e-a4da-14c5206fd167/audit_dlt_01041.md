# [M] IPFS go-bitfield vulnerable to DoS via malformed size arguments

## Summary
Severity: Medium
Chain: github.com/ipfs/go-bitfield
Component: github.com/ipfs/go-bitfield
CVE: CVE-2023-23626
CWE: Improper Check for Unusual or Exceptional Conditions, Improper Validation of Specified Quantity in Input
Published: 2023-02-10
Source: https://github.com/advisories/GHSA-2h6c-j3gf-xp9r
Type: github-advisory

## Details
### Impact
When feeding untrusted user input into the size parameter of `NewBitfield` and `FromBytes` functions, an attacker can trigger `panic`s.

This happen when the `size` is a not a multiple of `8` or is negative.
There were already a note in the `NewBitfield` documentation:
> ```
> Panics if size is not a multiple of 8.
> ````

But it incomplete and missing from `FromBytes`'s documentation.

This has been replaced by returning an `(Bitfield, error)` and returning a non nil error if the size is wrong.

### Patches
- https://github.com/ipfs/go-bitfield/commit/5e1d256fe043fc4163343ccca83862c69c52e579

### Workarounds
- Ensure `size%8 == 0 && size >= 0` yourself before calling `NewBitfield` or `FromBytes`

### References
- https://github.com/ipfs/go-unixfs/security/advisories/GHSA-q264-w97q-q778
