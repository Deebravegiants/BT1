# [H] CVE-2020-36323

## Summary
Severity: High
Advisory: CVE-2020-36323
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2021-04-14
Source: https://osv.dev/vulnerability/CVE-2020-36323
Type: osv

## Details
In the standard library in Rust before 1.52.0, there is an optimization for joining strings that can cause uninitialized bytes to be exposed (or the program to crash) if the borrowed string changes after its length is checked.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CZ337CM4GFJLRDFVQCGC7J25V65JXOG5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TFUO3URYCO73D2Q4WYJBWAMJWGGVXQO4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VZG65GUW6Z2CYOQHF7T3TB5CZKIX6ZJE/
- https://github.com/rust-lang/rust/issues/80335
- https://github.com/rust-lang/rust/pull/81728
- https://github.com/rust-lang/rust/pull/81728#issuecomment-821549174
- https://github.com/rust-lang/rust/pull/81728#issuecomment-824904190
