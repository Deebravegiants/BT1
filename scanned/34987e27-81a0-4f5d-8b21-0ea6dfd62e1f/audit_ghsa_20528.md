# [C] RPC call failure in ckb

## Summary
Severity: Critical
Advisory: GHSA-8gjm-h3xj-mp6w
CVE: CVE-2021-45698
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-8gjm-h3xj-mp6w
Type: github-advisory

## Affected
- crates.io: `ckb` — affected >=0 <0.40.0

## Details
An issue was discovered in the ckb crate before 0.40.0 for Rust. A get_block_template RPC call may fail in situations where it is supposed to select a Nervos CKB blockchain transaction with a higher fee rate than another transaction.

## References
- https://github.com/nervosnetwork/ckb/security/advisories/GHSA-v666-6w97-pcwm
- https://nvd.nist.gov/vuln/detail/CVE-2021-45698
- https://github.com/nervosnetwork/ckb
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/ckb/RUSTSEC-2021-0107.md
- https://rustsec.org/advisories/RUSTSEC-2021-0107.html
