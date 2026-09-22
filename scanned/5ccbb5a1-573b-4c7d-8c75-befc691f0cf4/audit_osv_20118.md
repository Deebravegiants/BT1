# [C] CVE-2021-31162

## Summary
Severity: Critical
Advisory: CVE-2021-31162
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/CVE-2021-31162
Type: osv

## Details
In the standard library in Rust before 1.52.0, a double free can occur in the Vec::from_iter function if freeing the element panics.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CZ337CM4GFJLRDFVQCGC7J25V65JXOG5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TFUO3URYCO73D2Q4WYJBWAMJWGGVXQO4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VZG65GUW6Z2CYOQHF7T3TB5CZKIX6ZJE/
- https://security.gentoo.org/glsa/202210-09
- https://github.com/rust-lang/rust/pull/83629
- https://github.com/rust-lang/rust/pull/84603
- https://github.com/rust-lang/rust/issues/83618
