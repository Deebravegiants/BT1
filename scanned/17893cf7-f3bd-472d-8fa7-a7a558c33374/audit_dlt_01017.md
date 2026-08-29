# [M] wasmvm: Malicious smart contract can slow down block production

## Summary
Severity: Medium
Chain: cosmwasm-vm
Component: cosmwasm-vm, cosmwasm-vm, cosmwasm-vm, cosmwasm-vm, github.com/CosmWasm/wasmvm/v2, github.com/CosmWasm/wasmvm/v2, github
Published: 2025-02-04
Source: https://github.com/advisories/GHSA-mx2j-7cmv-353c
Type: github-advisory

## Details
# CWA-2025-002

**Severity**

Medium (Moderate + Likely)[^1]

**Affected versions:**

- wasmvm >= 2.2.0, < 2.2.2
- wasmvm >= 2.1.0, < 2.1.5
- wasmvm >= 2.0.0, < 2.0.6
- wasmvm < 1.5.8

**Patched versions:**

- wasmvm 1.5.8, 2.0.6, 2.1.5, 2.2.2

## Description of the bug

The vulnerability can be used to slow down block production. The attack requires a malicious contract,
so permissioned chains are unlikely to be affected.

(We'll add more detail once chains had a chance to upgrade.)

## Patch

- 1.5: https://github.com/CosmWasm/cosmwasm/commit/2b7f2faa57a1efc8207455c37f87f1eee6035a27
- 2.0: https://github.com/CosmWasm/cosmwasm/commit/d6143b0aff16a39bbea4be37597d8e9d9b213d3b
- 2.1: https://github.com/CosmWasm/cosmwasm/commit/f0c04c03cbe2557634c1bbcdc2ce203fe7caca58
- 2.2: https://github.com/CosmWasm/cosmwasm/commit/a5d62f65b5eb947ebe40e2085b1c48a9d0a244d0

## Applying the patch

The patch will be shipped in releases of wasmvm. You can update more or less as follows:

1. Check the current wasmvm version: `go list -m github.com/CosmWasm/wasmvm`
2. Bump the `github.com/CosmWasm/wasmvm` dependency in your go.mod to one of the patched version
   depending on which minor version you are on; `go mod tidy`; commit.

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-mx2j-7cmv-353c_
