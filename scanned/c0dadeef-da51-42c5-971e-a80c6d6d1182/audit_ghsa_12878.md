# [H] bzip2 allows attackers to cause a denial of service via a large file that triggers an integer overflow

## Summary
Severity: High
Advisory: GHSA-96jv-r488-c2rj
CVE: CVE-2023-22895
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-10
Source: https://github.com/advisories/GHSA-96jv-r488-c2rj
Type: github-advisory

## Affected
- crates.io: `bzip2` — affected >=0 <0.4.4

## Details
The bzip2 crate before 0.4.4 for Rust allow attackers to cause a denial of service via a large file that triggers an integer overflow in `mem.rs`. NOTE: this is unrelated to the https://crates.io/crates/bzip2-rs product.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-22895
- https://github.com/alexcrichton/bzip2-rs/pull/86
- https://github.com/alexcrichton/bzip2-rs/commit/90c9c182cd5a5ebc75810aebd89b347a7bdf590b
- https://crates.io/crates/bzip2/versions
- https://github.com/alexcrichton/bzip2-rs
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MI5SVRSGKBWB2JGDLDVIFY5ZQVDZP6I7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SQK57GGXJX3AH7KF6S7S3N7JC5QOYUQ7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UUK2JO25PPA6XBREKJRBLRCD22LKIOLO
- https://rustsec.org/advisories/RUSTSEC-2023-0004.html
