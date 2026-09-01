# [M] `_validateSignature` doesn't check for deadline

## Summary
Severity: Medium
Chain: Smart contract
Component: Intuition
Published: 2024-06-22
Source: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/25
Type: hats-finding

## Details
**Github username:** @0x3b33
**Twitter username:** --
**Submission hash (on-chain):** 0xae191bb514c98b3f23817179d23e734dd39b9fed14fd1acd8880a73fa134c7a4
**Severity:** medium

**Description:**
**Description**\
`_validateSignature`, as documented by the [EIP-4337](https://eips.ethereum.org/EIPS/eip-4337) docs, MUST perform specific tasks to be compliant and safe.

One of these tasks is checking `validUntil` and `validAfter`, or in simple terms, determining **from when and up to when** the TX can be executed.

Without these checks, the signature is always valid, which can be dangerous as some executions are time-dependent.

**Example:**\
1. Alice sends a UserOperation to execute a swap, deposit, or withdraw.
2. The transaction sits in the mempool for a while.
3. The price of the asset changes.
4. The transaction finally gets executed, but at a worse price than Alice wanted.

In this case, Alice can lose some, if not all, of her funds if the transaction is executed too far into the future. Same can be said for `validAfter` in cases where the user wants to execute his TX after some X period of time.

**Attachments**\
Implement a deadline check that verifies if the signature is valid within the specified timeframe and reverts if it is not.
