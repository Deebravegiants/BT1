# [H] Data races in unicycle

## Summary
Severity: High
Advisory: GHSA-686f-ch3r-xwmh
CVE: CVE-2020-36436
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-686f-ch3r-xwmh
Type: github-advisory

## Affected
- crates.io: `unicycle` — affected >=0 <0.7.1

## Details
Affected versions of this crate unconditionally implemented `Send` & `Sync` for types `PinSlab<T>` & `Unordered<T, S>`. This allows sending non-Send types to other threads and concurrently accessing non-Sync types from multiple threads.

This can result in a data race & memory corruption when types that provide internal mutability without synchronization are contained within `PinSlab<T>` or `Unordered<T, S>` and accessed concurrently from multiple threads.

The flaw was corrected in commits 92f40b4 & 6a6c367 by adding trait bound `T: Send` to `Send` impls for `PinSlab<T>` & `Unordered<T, S>` and adding `T: Sync` to `Sync` impls for `PinSlab<T>` & `Unordered<T, S>`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36436
- https://github.com/udoprog/unicycle/issues/8
- https://github.com/udoprog/unicycle/commit/6a6c367a0c25f86f998fa315ea90c328f685b194
- https://github.com/udoprog/unicycle/commit/92f40b4a2c671553dfa96feacff0265206c44ce5
- https://github.com/udoprog/unicycle
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/unicycle/RUSTSEC-2020-0116.md
- https://rustsec.org/advisories/RUSTSEC-2020-0116.html
