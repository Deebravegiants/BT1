# [M] Use OpenZeppelin's SafeERC20

## Summary
Severity: Medium
Contest weight: 0.0508
Dataset id: 4381
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability stems from the contract calling ERC20 token functions transfer() and transferFrom() directly and assuming they follow the full ERC20 specification, namely that they return a boolean value indicating success and revert on failure. Some widely used tokens, such as USDT, deviate from the spec by not returning any value. When the contract does not check the return data, it may interpret a missing return as a successful call, even though the token transfer could have silently failed. This mismatch can be exploited by an attacker who deploys a malicious token that deliberately returns no value or returns false without reverting; the vulnerable contract will believe the transfer succeeded and may continue execution based on the false premise that it holds the transferred assets. Consequently, users may see a UI message indicating a successful deposit or withdrawal while their token balance remains unchanged, leading to accounting inconsistencies, potential loss of funds, or denial‑of‑service conditions where the protocol cannot progress because expected tokens were never received. The issue appears whenever the contract interacts with non‑standard ERC20 tokens and is discovered during manual audit review of token handling code. It is hard to notice because the transaction does not revert and no explicit error is emitted, so developers may assume normal operation. The proper mitigation is to replace raw calls with OpenZeppelin’s SafeERC20 library, using safeTransfer() and safeTransferFrom(), which internally verify the call success, handle missing return data, and revert on any failure, thereby restoring the intended safety guarantees of token transfers. This class of bug is commonly referred to as unchecked ERC20 return values or non‑standard token handling, and it violates the business logic that a successful transfer should result in the recipient’s balance increasing as expected.

## Recommendation
Consider using OpenZeppelin's SafeERC20's safeTransfer() and safeTransferFrom() functions instead of calling transfer() and transferFrom() on the token directly.
