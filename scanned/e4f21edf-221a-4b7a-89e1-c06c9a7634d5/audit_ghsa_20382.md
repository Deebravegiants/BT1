# [M] `MsQueue` `push`/`pop` use the wrong orderings

## Summary
Severity: Medium
Advisory: GHSA-rwf4-gx62-rqfw
Ecosystem: crates.io
Published: 2022-06-08
Source: https://github.com/advisories/GHSA-rwf4-gx62-rqfw
Type: github-advisory

## Affected
- crates.io: `crossbeam` — affected >=0 <0.3.0

## Details
Affected versions of this crate use orderings which are too weak to support this data structure.
It is likely this has caused memory corruption in the wild: <https://github.com/crossbeam-rs/crossbeam/issues/97#issuecomment-412785919>.

## References
- https://github.com/crossbeam-rs/crossbeam/issues/97#issuecomment-412785919
- https://github.com/crossbeam-rs/crossbeam/pull/98
- https://github.com/crossbeam-rs/crossbeam
- https://rustsec.org/advisories/RUSTSEC-2022-0029.html
