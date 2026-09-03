# [H] Specification non-compliance in JUMPI

## Summary
Severity: High
Chain: evm
Component: evm
CVE: CVE-2021-41153
CWE: Always-Incorrect Control Flow Implementation
Published: 2021-10-19
Source: https://github.com/advisories/GHSA-pvh2-pj76-4m96
Type: github-advisory

## Details
### Impact 

In `evm` crate `< 0.31.0`, `JUMPI` opcode's condition is checked after the destination validity check. However, according to Geth and OpenEthereum, the condition check should happen before the destination validity check.

### Patches

This is a **high** severity security advisory if you use `evm` crate for Ethereum mainnet. In this case, you should update your library dependency immediately to on or after `0.31.0`.

This is a **low** severity security advisory if you use `evm` crate in Frontier or in a standalone blockchain, because there's no security exploit possible with this advisory. It is **not** recommended to update to on or after `0.31.0` until all the normal chain upgrade preparations have been done. If you use Frontier or other `pallet-evm` based Substrate blockchain, please ensure to update your `spec_version` before updating this. For other blockchains, please make sure to follow a hard-fork process before you update this.

### Workarounds

If you are dependent on an older version of `evm` and cannot update due to API interface changes, please contact Wei by email (wei@that.world), who will be happy to help you to publish patch releases for older `evm` versions.

### References

Fix PR: https://github.com/rust-blockchain/evm/pull/67

### For more information

If you have any questions or comments about this advisory:
* Open an issue in the `evm` repo.

### Special thanks

Special thanks to @rakita for reporting this issue.
