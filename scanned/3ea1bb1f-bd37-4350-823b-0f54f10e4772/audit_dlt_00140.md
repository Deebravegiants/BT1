# [M] GovernorCompatibilityBravo incorrect ABI encoding may lead to unexpected behavior

## Summary
Severity: Medium
Chain: Solidity
Component: OpenZeppelin/openzeppelin-contracts
Published: 2022-01-11
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-m6w8-fq7v-ph4m
Type: github-advisory

## Details
### Impact

The `GovernorCompatibilityBravo` module may lead to the creation of governance proposals that execute function calls with incorrect arguments due to bad ABI encoding. This happens if the proposal is created using explicit function signatures, e.g. a proposal to invoke the function `foo(uint256)` is created as `propose([target], [0], ["foo(uint256)"], ["0x00..01"])`. If the function selector is provided as part of the encoded proposal data the issue is not present, e.g. the same proposal is created as `propose([target], [0], ["0x2fbebd3800..01"])`, where `2fbebd38` is the function selector.

We've assessed the instances of this contract found on chain, and did not find any occurrence of this bug in the past. Proposal creation through Tally or OpenZeppelin Defender is not affected. The core `Governor` contract on its own is not affected.

### Patches

A fix is included in version v4.4.2 of `@openzeppelin/contracts` and `@openzeppelin/contracts-upgradeable`.

### Workarounds

Do not create proposals using explicit function signatures. Instead, use the `propose` function without the `signatures` argument, and create the proposal using the fully ABI-encoded function call including the function selector in the `calldatas` argument as explained above.

### References

https://github.com/OpenZeppelin/openzeppelin-contracts/issues/3099

### Credits

This issue was identified and reported by @GeraldHost.

### For more information

If you have any questions, comments, or need assistance regarding this advisory, email us at security@openzeppelin.com.

To submit security reports please use [our bug bounty on Immunefi](https://immunefi.com/bounty/openzeppelin/).
