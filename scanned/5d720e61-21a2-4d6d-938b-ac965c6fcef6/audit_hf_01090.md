# [H] Lack of receive() function

## Summary
Severity: High
Contest weight: 0.7072
Dataset id: 4160
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract implements an unwrapEthOutput function that calls the WETH token’s withdraw method to convert all wrapped Ether held by the contract into native Ether. The withdraw call attempts to send Ether to the contract address itself. Because the contract does not define a receive() or payable fallback function, it is unable to accept incoming Ether transfers. When the WETH contract executes the low‑level call that delivers Ether, the call reverts due to the lack of a payable entry point, causing the entire unwrapEthOutput transaction to fail. This failure prevents users from receiving the expected Ether, effectively locking the converted funds inside the contract. The issue originates from a missing payable fallback, a common class of bug where contracts are not prepared to handle plain Ether transfers. It manifests whenever the unwrap function is invoked, or any other operation that results in the contract receiving Ether, such as direct transfers or other token withdrawals. Users attempting to unwrap their WETH see their transaction revert, receive no Ether, and may observe that their balance remains unchanged despite a successful WETH withdrawal call. The problem was discovered during a manual audit that inspected the contract’s external functions and noted the absence of a receive() implementation. Because the revert occurs only at runtime, it can be difficult to spot without testing the withdrawal path, and the UI may simply report a generic failure without indicating the underlying cause. To remediate the issue, the contract should include a receive() external payable {} (or a payable fallback) so that it can accept Ether sent by the WETH contract, allowing the unwrap operation to complete and funds to be released to the caller. Adding this payable entry point restores the intended business logic of converting WETH to Ether and prevents denial‑of‑service conditions where funds become permanently inaccessible.

## Recommendation
```solidity
receive() external payable {}
```
