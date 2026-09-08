# [H] Data races in tiny_future

## Summary
Severity: High
Advisory: GHSA-m296-j53x-xv95
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-m296-j53x-xv95
Type: github-advisory

## Affected
- crates.io: `tiny_future` — affected >=0 <0.4.0

## Details
`tiny_future` contains a light-weight implementation of `Future`s. The `Future` type it has lacked bound on its `Send` and `Sync` traits. This allows for a bug where non-thread safe types such as `Cell` can be used in `Future`s and cause data races in concurrent programs. The flaw was corrected in commit `c791919` by adding trait bounds to `Future`'s `Send` and `Sync`.

## References
- https://github.com/KizzyCode/tiny_future/issues/1
- https://github.com/KizzyCode/tiny_future/commit/7ab8a264980d23c2ed64e72f4636f38b7381eb39
- https://github.com/KizzyCode/tiny_future/commit/c7919199a0f6d1ce0e3c33499d1b37f862c990e4
- https://github.com/KizzyCode/tiny_future
- https://rustsec.org/advisories/RUSTSEC-2020-0118.html
