# [M] CVE-2021-28876

## Summary
Severity: Medium
Advisory: CVE-2021-28876
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-04-11
Source: https://osv.dev/vulnerability/CVE-2021-28876
Type: osv

## Details
In the standard library in Rust before 1.52.0, the Zip implementation has a panic safety issue. It calls __iterator_get_unchecked() more than once for the same index when the underlying iterator panics (in certain conditions). This bug could lead to a memory safety violation due to an unmet safety requirement for the TrustedRandomAccess trait.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CZ337CM4GFJLRDFVQCGC7J25V65JXOG5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TFUO3URYCO73D2Q4WYJBWAMJWGGVXQO4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VZG65GUW6Z2CYOQHF7T3TB5CZKIX6ZJE/
- https://security.gentoo.org/glsa/202210-09
- https://github.com/rust-lang/rust/issues/81740
- https://github.com/rust-lang/rust/pull/81741
