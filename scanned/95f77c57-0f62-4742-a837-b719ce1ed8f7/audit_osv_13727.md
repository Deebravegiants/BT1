# [M] CVE-2018-25008

## Summary
Severity: Medium
Advisory: CVE-2018-25008
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/CVE-2018-25008
Type: osv

## Details
In the standard library in Rust before 1.29.0, there is weak synchronization in the Arc::get_mut method. This synchronization issue can be lead to memory safety issues through race conditions.

## References
- https://github.com/rust-lang/rust/issues/51780
- https://github.com/rust-lang/rust/pull/52031
