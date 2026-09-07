# [M] Gas mispricing in cosmwasm-vm

## Summary
Severity: Medium
Chain: cosmwasm-vm
Component: cosmwasm-vm, cosmwasm-vm, cosmwasm-vm, github.com/CosmWasm/wasmvm/v2, github.com/CosmWasm/wasmvm/v2, github.com/CosmWasm
CWE: Improper Restriction of Power Consumption
Published: 2024-08-08
Source: https://github.com/advisories/GHSA-rg2q-2jh9-447q
Type: github-advisory

## Details
**Component:** wasmvm
**Criticality:** Medium ([ACMv1](https://github.com/interchainio/security/blob/main/resources/CLASSIFICATION_MATRIX.md): I:Moderate; L:Likely)
**Patched versions:** wasmvm 1.5.4, 2.0.3, 2.1.2

Some Wasm operations take significantly more gas than our benchmarks indicated. This can lead to missing the [gas target](https://github.com/CosmWasm/cosmwasm/blob/e50490c4199a234200a497219b27f071c3409f58/docs/GAS.md#cosmwasm-gas-pricing) we defined by a factor of ~10x. This means a malicious contract could take 10 times as much time to execute as expected, which can be used to temporarily DoS a chain.

See [CWA-2024-004](https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2024-004.md) for more details.
