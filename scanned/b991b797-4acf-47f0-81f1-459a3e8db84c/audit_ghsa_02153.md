# [H] Data races in async-coap

## Summary
Severity: High
Advisory: GHSA-9j8q-m9x5-9g6j
CVE: CVE-2020-36444
CWE: CWE-119, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-9j8q-m9x5-9g6j
Type: github-advisory

## Affected
- crates.io: `async-coap` — affected >=0

## Details
An issue was discovered in the async-coap crate through 2020-12-08 for Rust. 
Affected versions of this crate implement Send/Sync for `ArcGuard<RC, T>` with no trait bounds on `RC`. This allows users to send `RC: !Send` to other threads and also allows users to concurrently access `Rc: !Sync` from multiple threads.

This can result in memory corruption from data race or other undefined behavior caused by sending `T: !Send` to other threads (e.g. dropping `MutexGuard<T>` in another thread that didn't lock its mutex).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36444
- https://github.com/google/rust-async-coap/issues/33
- https://github.com/google/rust-async-coap
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/async-coap/RUSTSEC-2020-0124.md
- https://rustsec.org/advisories/RUSTSEC-2020-0124.html
