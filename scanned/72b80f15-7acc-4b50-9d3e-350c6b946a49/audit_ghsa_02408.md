# [M] Observable Discrepancy in libsecp256k1-rs

## Summary
Severity: Medium
Advisory: GHSA-7cqg-8449-rmfv
CVE: CVE-2019-20399
CWE: CWE-203, CWE-362
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-7cqg-8449-rmfv
Type: github-advisory

## Affected
- crates.io: `libsecp256k1-rs` — affected >=0 <0.3.1

## Details
A timing vulnerability in the Scalar::check_overflow function in Parity libsecp256k1-rs before 0.3.1 potentially allows an attacker to leak information via a side-channel attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20399
- https://github.com/paritytech/libsecp256k1/commit/11ba23a9766a5079918cd9f515bc100bc8164b50
- https://rustsec.org/advisories/RUSTSEC-2020-0156.html
