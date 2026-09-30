# [H] MongoDB Rust Driver has certificate validation disabled when `tlsInsecure=False` appears in connection string

## Summary
Severity: High
Advisory: GHSA-3p6w-gv5g-xjw9
CVE: CVE-2025-11695
CWE: CWE-295
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-3p6w-gv5g-xjw9
Type: github-advisory

## Affected
- crates.io: `mongodb` — affected >=0 <3.2.5

## Details
When tlsInsecure=False appears in a connection string, certificate validation is disabled.

This vulnerability affects MongoDB Rust Driver versions prior to v3.2.5.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11695
- https://github.com/mongodb/mongo-rust-driver/pull/1453
- https://github.com/mongodb/mongo-rust-driver/commit/21ed6aeeea386628621b36a6af2a1a248cc87dcf
- https://github.com/mongodb/mongo-rust-driver/commit/b918cd6676331c45f26dd1acd13e230aaf17fe6d
- https://github.com/mongodb/mongo-rust-driver
- https://jira.mongodb.org/browse/RUST-2264
