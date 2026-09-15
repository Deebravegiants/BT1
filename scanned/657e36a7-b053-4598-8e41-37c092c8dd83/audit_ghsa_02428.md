# [H] Double free in algorithmica

## Summary
Severity: High
Advisory: GHSA-jh37-772x-4hpw
CVE: CVE-2021-31996
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-jh37-772x-4hpw
Type: github-advisory

## Affected
- crates.io: `algorithmica` — affected >=0

## Details
An issue was discovered in the algorithmica crate through 2021-03-07 for Rust. In the affected versions of this crate, `merge_sort::merge()` wildly duplicates and drops ownership of `T` without guarding against double-free. Due to such implementation, simply invoking `merge_sort::merge()` on `Vec<T: Drop>` can cause **double free** bugs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31996
- https://github.com/AbrarNitk/algorithmica/issues/1
- https://rustsec.org/advisories/RUSTSEC-2021-0053.html
