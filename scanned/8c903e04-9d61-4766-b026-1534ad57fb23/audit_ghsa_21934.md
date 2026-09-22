# [H] crossbeam-utils Unsoundness of AtomicCell<{i,u}64> arithmetics on 32-bit targets that support Atomic{I,U}64

## Summary
Severity: High
Advisory: GHSA-qc84-gqf4-9926
CVE: CVE-2022-23639
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-qc84-gqf4-9926
Type: github-advisory

## Affected
- crates.io: `crossbeam-utils` — affected >=0 <0.8.7

## Details
### Impact

The affected versions of this crate incorrectly assumed that the alignment of `{i,u}64` was always the same as `Atomic{I,U}64`. 

However, the alignment of `{i,u}64` on a 32-bit target can be smaller than `Atomic{I,U}64`.

This can cause the following problems:

- Unaligned memory accesses
- Data race

Crates using `fetch_*` methods with `AtomicCell<{i,u}64>` are affected by this issue.

32-bit targets without `Atomic{I,U}64` and 64-bit targets are not affected by this issue.
32-bit targets with `Atomic{I,U}64` and `{i,u}64` have the same alignment are also not affected by this issue.

The following is a complete list of the builtin targets that may be affected. (last update: nightly-2022-02-11)

- armv7-apple-ios (tier 3)
- armv7s-apple-ios (tier 3)
- i386-apple-ios (tier 3)
- i586-unknown-linux-gnu
- i586-unknown-linux-musl
- i686-apple-darwin (tier 3)
- i686-linux-android
- i686-unknown-freebsd
- i686-unknown-haiku (tier 3)
- i686-unknown-linux-gnu
- i686-unknown-linux-musl
- i686-unknown-netbsd (tier 3)
- i686-unknown-openbsd (tier 3)
- i686-wrs-vxworks (tier 3)

([script to get list](https://gist.github.com/taiki-e/3c7891e8c5f5e0cbcb44d7396aabfe10))

### Patches

This has been fixed in crossbeam-utils 0.8.7.

Affected 0.8.x releases have been yanked.

### References

https://github.com/crossbeam-rs/crossbeam/pull/781 

### License

This advisory is in the public domain.

## References
- https://github.com/crossbeam-rs/crossbeam/security/advisories/GHSA-qc84-gqf4-9926
- https://nvd.nist.gov/vuln/detail/CVE-2022-23639
- https://github.com/crossbeam-rs/crossbeam/pull/781
- https://github.com/crossbeam-rs/crossbeam
- https://github.com/crossbeam-rs/crossbeam/releases/tag/crossbeam-utils-0.8.7
- https://rustsec.org/advisories/RUSTSEC-2022-0041.html
