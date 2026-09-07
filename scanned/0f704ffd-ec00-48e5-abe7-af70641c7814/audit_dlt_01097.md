# [M] Memory over-allocation in evm-core

## Summary
Severity: Medium
Chain: evm-core
Component: evm-core, evm-core, evm-core, evm-core, evm-core
CWE: Memory Allocation with Excessive Size Value
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-773q-5334-5gf9
Type: github-advisory

## Details
Prior to the patch, when executing specific EVM opcodes related
to memory operations that use `evm_core::Memory::copy_large`, the
crate can over-allocate memory when it is not needed, making it
possible for an attacker to perform denial-of-service attack.

The flaw was corrected in commit `19ade85`.
