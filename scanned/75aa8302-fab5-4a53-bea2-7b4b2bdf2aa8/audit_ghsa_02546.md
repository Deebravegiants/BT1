# [M] Data races in appendix

## Summary
Severity: Medium
Advisory: GHSA-fvhr-7j8m-3cvc
CVE: CVE-2020-36469
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-fvhr-7j8m-3cvc
Type: github-advisory

## Affected
- crates.io: `appendix` — affected >=0

## Details
The `appendix` crate implements a key-value mapping data structure called
`Index<K, V>` that is stored on disk. The crate allows for any type to inhabit
the generic `K` and `V` type parameters and implements Send and Sync for them
unconditionally.

Using a type that is not marked as `Send` or `Sync` with `Index` can allow it
to be used across multiple threads leading to data races. Additionally using
reference types for the keys or values will lead to the segmentation faults
in the crate's code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36469
- https://github.com/krl/appendix/issues/6
- https://github.com/krl/appendix
- https://rustsec.org/advisories/RUSTSEC-2020-0149.html
