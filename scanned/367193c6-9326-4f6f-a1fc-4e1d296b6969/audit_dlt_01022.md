# [M] CWA-2023-004: Excessive number of function parameters in compiled Wasm

## Summary
Severity: Medium
Chain: cosmwasm-vm
Component: cosmwasm-vm, cosmwasm-vm, cosmwasm-vm, cosmwasm-vm, github.com/CosmWasm/wasmvm, github.com/CosmWasm/wasmvm, github.com/C
CWE: Uncontrolled Resource Consumption
Published: 2024-08-27
Source: https://github.com/advisories/GHSA-75qh-gg76-p2w4
Type: github-advisory

## Details
A specifically crafted Wasm file can cause the VM to consume excessive amounts of memory when compiling a contract.
This can lead to high memory usage, slowdowns, potentially a crash and can poison a lock in the VM,
preventing any further interaction with contracts.

For more information, see [CWA-2023-004](https://github.com/CosmWasm/advisories/blob/main/CWAs/CWA-2023-004.md).
