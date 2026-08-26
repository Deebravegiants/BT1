# [M] CosmWasm VM Incorrect metering

## Summary
Severity: Medium
Chain: github.com/CosmWasm/wasmvm/v2
Component: github.com/CosmWasm/wasmvm/v2, github.com/CosmWasm/wasmvm/v2, github.com/CosmWasm/wasmvm, cosmwasm-vm, cosmwasm-vm, cosm
Published: 2024-12-10
Source: https://github.com/advisories/GHSA-2q97-m5rc-p3gp
Type: github-advisory

## Details
# CWA-2024-007

**Severity**

Medium (Moderate + Likely)[^1]

**Affected versions:**

- wasmvm >= 2.1.0, < 2.1.3
- wasmvm >= 2.0.0, < 2.0.4
- wasmvm < 1.5.5
- cosmwasm-vm >= 2.1.0, < 2.1.4
- cosmwasm-vm >= 2.0.0, < 2.0.7
- cosmwasm-vm < 1.5.8

**Patched versions:**

- wasmvm 1.5.5, 2.0.4, 2.1.3
- cosmwasm-vm 1.5.8, 2.0.7, 2.1.4

## Description of the bug

(Blank for now. We'll add more detail once chains had a chance to upgrade.)

## Patch

- 1.5: https://github.com/CosmWasm/cosmwasm/commit/16eabd681790508b13dac8e67f9e6e61045240ea
- 2.0: https://github.com/CosmWasm/cosmwasm/commit/0e70bd83119b02f99a2c0397f0913e0803750fd9
- 2.1: https://github.com/CosmWasm/cosmwasm/commit/f5bf24f3acadca2892afd58cc3ce5fdeb932d492

## Applying the patch

The patch will be shipped in releases of wasmvm. You can update more or less as follows:

1. Check the current wasmvm version: `go list -m github.com/CosmWasm/wasmvm`
2. Bump the `github.com/CosmWasm/wasmvm` dependency in your go.mod to 1.5.5, 2.0.4, 2.1.3 depending on which minor version you are; `go mod tidy`; commit.
3. If you use the static libraries `libwasmvm_muslc.aarch64.a`/`libwasmvm_muslc.x86_64.a`, update them accordingly.
4. Check the updated wasmvm version: `go list -m github.com/CosmWasm/wasmvm` and ensure you see 1.5.5, 2.0.4, 2.1.3.

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-2q97-m5rc-p3gp_
