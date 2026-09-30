# [M] CWA-2024-004: Gas mispricing in cosmwasm-vm

## Summary
Severity: Medium
Advisory: RUSTSEC-2024-0361
Aliases: GHSA-rg2q-2jh9-447q
Package: cosmwasm-vm
Published: 2024-08-08
Source: https://osv.dev/vulnerability/RUSTSEC-2024-0361
Type: chain-advisory

## Affected
- crates.io: `cosmwasm-vm` — affected >=2.1.0 <2.1.3

## Details
Some Wasm operations take significantly more gas than our benchmarks indicated. This can lead to missing the gas target we defined by a factor of ~10x. This means a malicious contract could take 10 times as much time to execute as expected, which can be used to temporarily DoS a chain.

For more information, see [CWA-2024-004](https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2024-004.md).

## References
- https://crates.io/crates/cosmwasm-vm
- https://rustsec.org/advisories/RUSTSEC-2024-0361.html
- https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2024-004.md
