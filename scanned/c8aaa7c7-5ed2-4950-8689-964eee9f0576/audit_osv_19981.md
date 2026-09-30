# [C] CVE-2021-28879

## Summary
Severity: Critical
Advisory: CVE-2021-28879
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-11
Source: https://osv.dev/vulnerability/CVE-2021-28879
Type: osv

## Details
In the standard library in Rust before 1.52.0, the Zip implementation can report an incorrect size due to an integer overflow. This bug can lead to a buffer overflow when a consumed Zip iterator is used again.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CZ337CM4GFJLRDFVQCGC7J25V65JXOG5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TFUO3URYCO73D2Q4WYJBWAMJWGGVXQO4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VZG65GUW6Z2CYOQHF7T3TB5CZKIX6ZJE/
- https://security.gentoo.org/glsa/202210-09
- https://github.com/rust-lang/rust/issues/82282
- https://github.com/rust-lang/rust/pull/82289
