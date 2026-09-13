# [M] Gas mispricing in cosmwasm-vm

## Summary
Severity: Medium
Advisory: GHSA-rg2q-2jh9-447q
CWE: CWE-920
Ecosystem: Go, crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-08-08
Source: https://github.com/advisories/GHSA-rg2q-2jh9-447q
Type: github-advisory

## Affected
- crates.io: `cosmwasm-vm` — affected >=0 <1.5.6
- crates.io: `cosmwasm-vm` — affected >=2.0.0 <2.0.5
- crates.io: `cosmwasm-vm` — affected >=2.1.0 <2.1.2
- Go: `github.com/CosmWasm/wasmvm/v2` — affected >=2.1.0 <2.1.2
- Go: `github.com/CosmWasm/wasmvm/v2` — affected >=2.0.0 <2.0.3
- Go: `github.com/CosmWasm/wasmvm` — affected >=0 <1.5.4

## Details
**Component:** wasmvm
**Criticality:** Medium ([ACMv1](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md): I:Moderate; L:Likely)
**Patched versions:** wasmvm 1.5.4, 2.0.3, 2.1.2

Some Wasm operations take significantly more gas than our benchmarks indicated. This can lead to missing the [gas target](https://github.com/CosmWasm/cosmwasm/blob/e50490c4199a234200a497219b27f071c3409f58/docs/GAS.md#cosmwasm-gas-pricing) we defined by a factor of ~10x. This means a malicious contract could take 10 times as much time to execute as expected, which can be used to temporarily DoS a chain.

See [CWA-2024-004](https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2024-004.md) for more details.

## References
- https://github.com/CosmWasm/wasmvm/security/advisories/GHSA-rg2q-2jh9-447q
- https://github.com/CosmWasm/cosmwasm/commit/5bef1c588933bd60a04bb70099150cf84b69e144
- https://github.com/CosmWasm/cosmwasm/commit/9b4d6d03772b75d500a7d3c972d0d8ba6d085c06
- https://github.com/CosmWasm/cosmwasm/commit/c1313afeb261e17b1c8cf6a1eacee1da0dac42ae
- https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2024-004.md
- https://github.com/CosmWasm/wasmvm
- https://rustsec.org/advisories/RUSTSEC-2024-0361.html
