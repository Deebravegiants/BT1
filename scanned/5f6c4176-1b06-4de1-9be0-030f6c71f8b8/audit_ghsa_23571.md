# [M] Exposure of Sensitive Information to an Unauthorized Actor in MongoDB Rust Driver

## Summary
Severity: Medium
Advisory: GHSA-4rjr-3gj2-5crq
CVE: CVE-2021-20332
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4rjr-3gj2-5crq
Type: github-advisory

## Affected
- crates.io: `mongodb` — affected >=1.0.0 <2.0.0-beta

## Details
Specific MongoDB Rust Driver versions can include credentials used by the connection pool to authenticate connections in the monitoring event that is emitted when the pool is created. The user's logging infrastructure could then potentially ingest these events and unexpectedly leak the credentials. Note that such monitoring is not enabled by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20332
- https://github.com/mongodb/mongo-rust-driver/commit/9e8782b1bb1104e5399c073b553719c262d4463c
- https://github.com/mongodb/mongo-rust-driver
- https://jira.mongodb.org/browse/RUST-591
