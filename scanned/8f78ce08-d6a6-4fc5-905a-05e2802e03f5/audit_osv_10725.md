# [M] CVE-2017-20004

## Summary
Severity: Medium
Advisory: CVE-2017-20004
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/CVE-2017-20004
Type: osv

## Details
In the standard library in Rust before 1.19.0, there is a synchronization problem in the MutexGuard object. MutexGuards can be used across threads with any types, allowing for memory safety issues through race conditions.

## References
- https://github.com/rust-lang/rust/issues/41622
- https://github.com/rust-lang/rust/pull/41624
