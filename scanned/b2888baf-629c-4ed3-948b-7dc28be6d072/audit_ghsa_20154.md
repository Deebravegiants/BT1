# [H] Unsoundness in `dashmap` references

## Summary
Severity: High
Advisory: GHSA-mpg5-fvwp-42m2
Ecosystem: crates.io
Published: 2022-06-16
Source: https://github.com/advisories/GHSA-mpg5-fvwp-42m2
Type: github-advisory

## Affected
- crates.io: `dashmap` — affected >=5.0.0 <5.1.0

## Details
Reference returned by some methods of `Ref` (and similar types) may outlive the `Ref` and escape the lock.
This causes undefined behavior and may result in a segfault.

More information in [`dashmap#167`](https://github.com/xacrimon/dashmap/issues/167) issue.

## References
- https://github.com/xacrimon/dashmap/issues/167
- https://github.com/xacrimon/dashmap
- https://rustsec.org/advisories/RUSTSEC-2022-0002.html
