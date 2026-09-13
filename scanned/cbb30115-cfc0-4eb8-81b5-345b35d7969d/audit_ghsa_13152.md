# [M] Users vulnerable to unaligned read of `*const *const c_char` pointer

## Summary
Severity: Medium
Advisory: GHSA-jcr6-4frq-9gjj
Ecosystem: crates.io
Published: 2023-09-11
Source: https://github.com/advisories/GHSA-jcr6-4frq-9gjj
Type: github-advisory

## Affected
- crates.io: `users` — affected >=0

## Details
Affected versions dereference a potentially unaligned pointer. The pointer is commonly unaligned in practice, resulting in undefined behavior.

In some build modes, this is observable as a panic followed by abort. In other build modes the UB may manifest in some other way, including the possibility of working correctly in some architectures.

The crate is not currently maintained, so a patched version is not available.

## Recommended alternatives
- [`uzers`](https://crates.io/crates/uzers) (an actively maintained fork of the `users` crate)
- [`sysinfo`](https://crates.io/crates/sysinfo)

## References
- https://github.com/ogham/rust-users/issues/55
- https://github.com/ogham/rust-users
- https://rustsec.org/advisories/RUSTSEC-2023-0059.html
