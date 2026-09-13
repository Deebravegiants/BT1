# [H] Out of bounds write in reorder

## Summary
Severity: High
Advisory: GHSA-jpwg-6gf5-5vh9
CVE: CVE-2021-29942
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-jpwg-6gf5-5vh9
Type: github-advisory

## Affected
- crates.io: `reorder` — affected >=0 <1.1.0

## Details
swap_index takes an iterator and swaps the items with their corresponding indexes. It reserves capacity and sets the length of the vector based on the .len() method of the iterator.

If the len() returned by the iterator is larger than the actual number of elements yielded, then swap_index creates a vector containing uninitialized members. If the len() returned by the iterator is smaller than the actual number of members yielded, then swap_index can write out of bounds past its allocated vector.

As noted by the Rust documentation, len() and size_hint() are primarily meant for optimization and incorrect values from their implementations should not lead to memory safety violations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-29942
- https://github.com/tiby312/reorder/issues/1
- https://github.com/tiby312/reorder
- https://rustsec.org/advisories/RUSTSEC-2021-0050.html
