# [H] Data races in beef

## Summary
Severity: High
Advisory: GHSA-m7w4-8wp8-m2xq
CVE: CVE-2020-36442
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-m7w4-8wp8-m2xq
Type: github-advisory

## Affected
- crates.io: `beef` — affected >=0 <0.5.0

## Details
An issue was discovered in the beef crate before 0.5.0 for Rust. 
Affected versions of this crate did not have a `T: Sync` bound in the `Send` impl for `Cow<'_, T, U>`. This allows users to create data races by making `Cow` contain types that are (Send && !Sync) like `Cell<_>` or `RefCell<_>`.

Such data races can lead to memory corruption.

The flaw was corrected in commit d1c7658 by adding trait bounds `T: Sync` and `T::Owned: Send` to the `Send` impl for `Cow<'_, T, U>`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36442
- https://github.com/maciejhirsz/beef/issues/37
- https://github.com/maciejhirsz/beef
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/beef/RUSTSEC-2020-0122.md
- https://rustsec.org/advisories/RUSTSEC-2020-0122.html
