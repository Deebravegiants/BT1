# [M] Partial read is incorrect in molecule

## Summary
Severity: Medium
Advisory: GHSA-82hm-vh7g-hrh9
Ecosystem: crates.io
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-82hm-vh7g-hrh9
Type: github-advisory

## Affected
- crates.io: `molecule` — affected >=0 <0.7.2

## Details
### Impact

Anyone who uses `total_size(..)` function to partial read the length of any `FixVec` will get an incorrect result, due to an incorrect implementation. This has been resolved in the 0.7.2 release.

### Workarounds

If you already have the whole `FixVec` `A`, you can use `A.as_slice().len()` to get the total size of the `FixVec`.

### For more information

If you have any questions or comments about this advisory:

- [Open an issue to ask use directly](https://github.com/nervosnetwork/molecule/issues/new).

## References
- https://github.com/nervosnetwork/molecule/security/advisories/GHSA-82hm-vh7g-hrh9
- https://github.com/nervosnetwork/molecule/pull/49
- https://github.com/nervosnetwork/molecule
- https://rustsec.org/advisories/RUSTSEC-2021-0103.html
