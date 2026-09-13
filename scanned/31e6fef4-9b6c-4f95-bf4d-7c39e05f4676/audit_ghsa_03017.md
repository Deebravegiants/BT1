# [M] Unexpected panics in num-bigint

## Summary
Severity: Medium
Advisory: GHSA-v935-pqmr-g8v9
CWE: CWE-131, CWE-20
Ecosystem: crates.io
Published: 2021-11-03
Source: https://github.com/advisories/GHSA-v935-pqmr-g8v9
Type: github-advisory

## Affected
- crates.io: `num-bigint` — affected >=0.4.1 <0.4.3

## Details
### Impact

Two scenarios were reported where `BigInt` and `BigUint` multiplication may unexpectedly panic.

- The internal `mac3` function did not expect the possibility of non-empty all-zero inputs, leading to an `unwrap()` panic.
- A buffer was allocated with less capacity than needed for an intermediate result, leading to an assertion panic.

Rust panics can either cause stack unwinding or program abort, depending on the application configuration. In some settings, an unexpected panic may constitute a denial-of-service vulnerability.

### Patches
Both problems were introduced in version 0.4.1, and are fixed in version 0.4.3.

### For more information
If you have any questions or comments about this advisory, please open an issue in the [num-bigint](https://github.com/rust-num/num-bigint) repo.

### Acknowledgements
Thanks to Guido Vranken and Arvid Norberg for privately reporting these issues to the author.

### References
* [GHSA-v935-pqmr-g8v9](https://github.com/rust-num/num-bigint/security/advisories/GHSA-v935-pqmr-g8v9)
* [num-bigint#228](https://github.com/rust-num/num-bigint/pull/228)

## References
- https://github.com/rust-num/num-bigint/security/advisories/GHSA-v935-pqmr-g8v9
- https://github.com/rust-num/num-bigint/pull/228
- https://github.com/rust-num/num-bigint
