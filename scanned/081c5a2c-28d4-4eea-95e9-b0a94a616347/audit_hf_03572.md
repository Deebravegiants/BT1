# [M] Return values of `transfer`

## Summary
Severity: Medium
Contest weight: 0.0381
Dataset id: 19474
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability concerns the handling of the return value from an ERC‑20 token's transfer function. In the examined contract the code invokes token.transfer(recipient, amount) but does not verify the boolean value that the function returns. The root cause is the assumption that the transfer will always succeed, which is not guaranteed by the ERC‑20 specification; a compliant token may return false to indicate a failed transfer without reverting. Because the contract proceeds without checking this flag, it may treat a failed transfer as successful, leading to an inconsistent internal accounting state. An attacker controlling a malicious token contract could deliberately cause transfer to return false while still deducting allowance or could simply return false without moving tokens, causing the calling contract to believe funds were moved when they were not. The impact is that users may see their balances unchanged or may receive no tokens despite the contract recording a successful operation, effectively resulting in lost or locked funds and broken business logic such as refunds, payouts, or staking rewards. This condition occurs every time the contract performs a token transfer without a require or SafeERC20 wrapper, i.e., under any execution path that triggers the unchecked call. The affected parties are the contract’s users, the protocol that relies on correct token accounting, and any downstream contracts that assume the transfer succeeded. The issue was identified by an automated static analysis tool that flagged the missing check as a medium‑severity finding. It can be hard to notice because the transaction does not revert; the UI may show a successful transaction hash while the token balance remains unchanged, leading to confusion. To remediate, the contract should explicitly verify the boolean result (e.g., require(token.transfer(...))) or, preferably, use a well‑audited library such as OpenZeppelin's SafeERC20 which reverts on false returns. This class of bug is commonly referred to as an unchecked return‑value vulnerability in token transfers and violates the fundamental accounting assumption that a transfer either succeeds or reverts, not silently fail.

## Recommendation
No recommendation
