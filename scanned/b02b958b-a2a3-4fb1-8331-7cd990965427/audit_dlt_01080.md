# [M] Memory over-allocation in evm crate

## Summary
Severity: Medium
Chain: evm
Component: evm, evm-core, evm, evm, evm, evm, evm, evm-core, evm-core, evm-core, evm-core, evm-core
CVE: CVE-2021-29511
CWE: Allocation of Resources Without Limits or Throttling, Out-of-bounds Write
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-4jwq-572w-4388
Type: github-advisory

## Details
### Impact
Prior to the patch, when executing specific EVM opcodes related to memory operations that use `evm_core::Memory::copy_large`, the crate can over-allocate memory when it is not needed, making it possible for an attacker to perform denial-of-service attack.

### Patches
The flaw was corrected in commit `19ade85`. Users should upgrade to `==0.21.1, ==0.23.1, ==0.24.1, ==0.25.1, >=0.26.1`.

### Workarounds
None. Please upgrade your `evm` crate version

### References
Fix commit: https://github.com/rust-blockchain/evm/commit/19ade858c430ab13eb562764a870ac9f8506f8dd

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [evm repo](https://github.com/rust-blockchain/evm)
* Email [Wei](mailto:wei@that.world)
