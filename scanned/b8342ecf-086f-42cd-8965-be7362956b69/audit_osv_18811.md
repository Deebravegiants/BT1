# [C] CVE-2020-36318

## Summary
Severity: Critical
Advisory: CVE-2020-36318
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-11
Source: https://osv.dev/vulnerability/CVE-2020-36318
Type: osv

## Details
In the standard library in Rust before 1.49.0, VecDeque::make_contiguous has a bug that pops the same element more than once under certain condition. This bug could result in a use-after-free or double free.

## References
- https://github.com/rust-lang/rust/issues/79808
- https://github.com/rust-lang/rust/pull/79814
