# [H] CVE-2021-28875

## Summary
Severity: High
Advisory: CVE-2021-28875
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-11
Source: https://osv.dev/vulnerability/CVE-2021-28875
Type: osv

## Details
In the standard library in Rust before 1.50.0, read_to_end() does not validate the return value from Read in an unsafe context. This bug could lead to a buffer overflow.

## References
- https://security.gentoo.org/glsa/202210-09
- https://github.com/rust-lang/rust/issues/80894
- https://github.com/rust-lang/rust/pull/80895
