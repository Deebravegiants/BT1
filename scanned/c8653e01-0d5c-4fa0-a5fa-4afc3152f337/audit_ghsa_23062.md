# [H] Integer overflow in solana_rbpf

## Summary
Severity: High
Advisory: GHSA-ffx3-8qvm-pq3j
CVE: CVE-2022-31264
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-22
Source: https://github.com/advisories/GHSA-ffx3-8qvm-pq3j
Type: github-advisory

## Affected
- crates.io: `solana_rbpf` — affected >=0 <0.2.29

## Details
Solana solana_rbpf before 0.2.29 has an addition integer overflow via invalid ELF program headers. elf.rs has a panic via a malformed eBPF program.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31264
- https://github.com/Ainevsia/CVE-Request/tree/main/Solana/1
- https://github.com/solana-labs/rbpf
- https://github.com/solana-labs/rbpf/releases/tag/v0.2.29
