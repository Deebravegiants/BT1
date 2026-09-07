# [H] Allocation of Resources Without Limits or Throttling in ckb

## Summary
Severity: High
Advisory: GHSA-2969-8hh9-57jc
CVE: CVE-2021-45699
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-2969-8hh9-57jc
Type: github-advisory

## Affected
- crates.io: `ckb` — affected >=0 <0.40.0

## Details
An issue was discovered in the ckb crate before 0.40.0 for Rust. Remote attackers may be able to conduct a 51% attack against the Nervos CKB blockchain by triggering an inability to allocate memory for the misbehavior HashMap.

## References
- https://github.com/nervosnetwork/ckb/security/advisories/GHSA-48vq-8jqv-gm6f
- https://nvd.nist.gov/vuln/detail/CVE-2021-45699
- https://github.com/nervosnetwork/ckb
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/ckb/RUSTSEC-2021-0108.md
- https://rustsec.org/advisories/RUSTSEC-2021-0108.html
