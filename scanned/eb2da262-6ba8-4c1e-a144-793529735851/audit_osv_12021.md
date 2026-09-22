# [H] CVE-2018-1000657

## Summary
Severity: High
Advisory: CVE-2018-1000657
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-1000657
Type: osv

## Details
Rust Programming Language Rust standard library version Commit bfa0e1f58acf1c28d500c34ed258f09ae021893e and later; stable release 1.3.0 and later contains a Buffer Overflow vulnerability in std::collections::vec_deque::VecDeque::reserve() function that can result in Arbitrary code execution, but no proof-of-concept exploit is currently published.. This vulnerability appears to have been fixed in after commit fdfafb510b1a38f727e920dccbeeb638d39a8e60; stable release 1.22.0 and later.

## References
- http://www.securityfocus.com/bid/105188
- https://github.com/rust-lang/rust/issues/44800
- https://github.com/rust-lang/rust/commit/f71b37bc28326e272a37b938e835d4f99113eec2
