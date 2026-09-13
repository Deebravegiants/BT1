# [C] Double free in smallvec

## Summary
Severity: Critical
Advisory: GHSA-rxr4-x558-x7hw
CVE: CVE-2018-20991
CWE: CWE-415
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-rxr4-x558-x7hw
Type: github-advisory

## Affected
- crates.io: `smallvec` — affected >=0.3.2 <0.6.3

## Details
If an iterator passed to SmallVec::insert_many panicked in Iterator::next, destructors were run during unwinding while the vector was in an inconsistent state, possibly causing a double free (a destructor running on two copies of the same value).

This is fixed in smallvec 0.6.3 by ensuring that the vector's length is not updated to include moved items until they have been removed from their original positions. Items may now be leaked if Iterator::next panics, but they will not be dropped more than once.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20991
- https://github.com/servo/rust-smallvec/issues/96
- https://github.com/servo/rust-smallvec
- https://rustsec.org/advisories/RUSTSEC-2018-0003.html
