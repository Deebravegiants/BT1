# [H] CVE-2020-36317

## Summary
Severity: High
Advisory: CVE-2020-36317
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-11
Source: https://osv.dev/vulnerability/CVE-2020-36317
Type: osv

## Details
In the standard library in Rust before 1.49.0, String::retain() function has a panic safety problem. It allows creation of a non-UTF-8 Rust string when the provided closure panics. This bug could result in a memory safety violation when other string APIs assume that UTF-8 encoding is used on the same string.

## References
- https://github.com/rust-lang/rust/issues/78498
- https://github.com/rust-lang/rust/pull/78499
