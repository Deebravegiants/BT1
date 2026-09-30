# [H] Integer overflow in solana_rbpf

## Summary
Severity: High
Advisory: GHSA-ffx3-8qvm-pq3j
Aliases: CVE-2022-31264
Package: solana_rbpf
Published: 2022-05-22
Source: https://osv.dev/vulnerability/GHSA-ffx3-8qvm-pq3j
Type: chain-advisory

## Affected
- crates.io: `solana_rbpf` — affected >=0 <0.2.29

## Details
Solana solana_rbpf before 0.2.29 has an addition integer overflow via invalid ELF program headers. elf.rs has a panic via a malformed eBPF program.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31264
- https://github.com/Ainevsia/CVE-Request/tree/main/Solana/1
- https://github.com/solana-labs/rbpf
- https://github.com/solana-labs/rbpf/releases/tag/v0.2.29
