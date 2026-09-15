# [H] Use of Uninitialized Resource in smallvec

## Summary
Severity: High
Advisory: GHSA-55m5-whcv-c49c
CVE: CVE-2018-25023
CWE: CWE-908
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-55m5-whcv-c49c
Type: github-advisory

## Affected
- crates.io: `smallvec` — affected >=0 <0.6.13

## Details
Affected versions of this crate called mem::uninitialized() to create values of a user-supplied type T. This is unsound e.g. if T is a reference type (which must be non-null and thus may not remain uninitialized). The flaw was corrected by avoiding the use of mem::uninitialized(), using MaybeUninit instead.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25023
- https://github.com/servo/rust-smallvec/issues/126
- https://github.com/servo/rust-smallvec/pull/162
- https://github.com/servo/rust-smallvec/commit/e64afc8c473d43e375ab42bd33db2d0d4ac4e41b
- https://github.com/servo/rust-smallvec
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/smallvec/RUSTSEC-2018-0018.md
- https://rustsec.org/advisories/RUSTSEC-2018-0018.html
