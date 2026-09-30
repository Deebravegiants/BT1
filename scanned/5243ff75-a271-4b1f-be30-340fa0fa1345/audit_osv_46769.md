# [H] CVE-2015-20001

## Summary
Severity: High
Advisory: CVE-2015-20001
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-11
Source: https://osv.dev/vulnerability/CVE-2015-20001
Type: osv

## Details
In the standard library in Rust before 1.2.0, BinaryHeap is not panic-safe. The binary heap is left in an inconsistent state when the comparison of generic elements inside sift_up or sift_down_range panics. This bug leads to a drop of zeroed memory as an arbitrary type, which can result in a memory safety violation.

## References
- https://github.com/rust-lang/rust/issues/25842
- https://github.com/rust-lang/rust/pull/25856
- https://github.com/rust-lang/rust/issues/25842
- https://github.com/rust-lang/rust/issues/25842
- https://github.com/rust-lang/rust/pull/25856
- https://github.com/rust-lang/rust/issues/25842
- https://github.com/rust-lang/rust/pull/25856
