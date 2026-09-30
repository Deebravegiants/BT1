# [M] MongoDB Rust driver may issue unintended commands

## Summary
Severity: Medium
Advisory: GHSA-32jf-h775-g29h
CVE: CVE-2024-6382
CWE: CWE-228
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2024-07-02
Source: https://github.com/advisories/GHSA-32jf-h775-g29h
Type: github-advisory

## Affected
- crates.io: `mongodb` — affected >=2.0.0 <2.8.2

## Details
Incorrect handling of certain string inputs may result in MongoDB Rust driver constructing unintended server commands. This may cause unexpected application behavior including data modification. This issue affects MongoDB Rust Driver 2.0 versions prior to 2.8.2

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6382
- https://github.com/mongodb/mongo-rust-driver/pull/1045
- https://github.com/mongodb/mongo-rust-driver/commit/8eac3bc6dc37a6d7667ed6c1a895c224e3ff47e1
- https://github.com/mongodb/mongo-rust-driver/commit/a3fe6c84ce6287348b1268f651fdac9fbed66187
- https://github.com/mongodb/mongo-rust-driver
- https://jira.mongodb.org/browse/RUST-1881
