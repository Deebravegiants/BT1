# [H] Denial of Service in ckb

## Summary
Severity: High
Advisory: GHSA-cw98-cx2m-9qqg
CVE: CVE-2021-45700
CWE: CWE-400
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-cw98-cx2m-9qqg
Type: github-advisory

## Affected
- crates.io: `ckb` — affected >=0 <0.40.0

## Details
An issue was discovered in the ckb crate before 0.40.0 for Rust. Attackers can cause a denial of service (Nervos CKB blockchain node crash) via a dead call that is used as a DepGroup.

## References
- https://github.com/nervosnetwork/ckb/security/advisories/GHSA-45p7-c959-rgcm
- https://nvd.nist.gov/vuln/detail/CVE-2021-45700
- https://github.com/nervosnetwork/ckb
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/ckb/RUSTSEC-2021-0109.md
- https://rustsec.org/advisories/RUSTSEC-2021-0109.html
