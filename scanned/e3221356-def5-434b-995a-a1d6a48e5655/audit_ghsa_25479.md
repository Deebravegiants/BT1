# [M] futures_task::noop_waker_ref can segfault due to dereferencing a NULL pointer

## Summary
Severity: Medium
Advisory: GHSA-p9m5-3hj7-cp5r
CVE: CVE-2020-35907
CWE: CWE-476
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p9m5-3hj7-cp5r
Type: github-advisory

## Affected
- crates.io: `futures-task` — affected >=0 <0.3.5

## Details
Affected versions of the crate used a UnsafeCell in thread-local storage to return a noop waker reference, assuming that the reference would never be returned from another thread.

This resulted in a segmentation fault crash if Waker::wake_by_ref() was called on a waker returned from another thread due to it attempting to dereference a pointer that wasn't accessible from the main thread.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35907
- https://github.com/rust-lang/futures-rs/issues/2091
- https://github.com/rust-lang/futures-rs
- https://rustsec.org/advisories/RUSTSEC-2020-0061.html
