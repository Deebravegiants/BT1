# [M] MutexGuard::map can cause a data race in safe code

## Summary
Severity: Medium
Advisory: GHSA-rh4w-94hh-9943
CVE: CVE-2020-35905
CWE: CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rh4w-94hh-9943
Type: github-advisory

## Affected
- crates.io: `futures-util` — affected >=0.3.2 <0.3.7

## Details
Affected versions of the crate had a Send/Sync implementation for MappedMutexGuard that only considered variance on T, while MappedMutexGuard dereferenced to U.

This could of led to data races in safe Rust code when a closure used in MutexGuard::map() returns U that is unrelated to T.

The issue was fixed by fixing Send and Sync implementations, and by adding a PhantomData<&'a mut U> marker to the MappedMutexGuard type to tell the compiler that the guard is over U too.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35905
- https://github.com/rust-lang/futures-rs/issues/2239
- https://github.com/rust-lang/futures-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0059.html
