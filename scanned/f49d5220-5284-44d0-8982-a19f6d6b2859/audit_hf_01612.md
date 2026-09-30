# [C] C-1 Several reentracy scenarios

## Summary
Severity: Critical
Contest weight: 0.2587
Dataset id: 8652
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The issue is identified within the LOB contract.
Some ERC-20 tokens implement extensions, such as the ERC-777 standard, that allow an account to gain execution control during token transfers. As the protocol is planned to be deployed on several networks and support various tokens, it may encounter issues related to these types of tokens.
If an attacker gains control during a token transfer, they can launch a "reentrancy" attack against the protocol by following these steps:
1. Set up send/receive hooks.
2. Perform an action that causes the protocol to send or receive tokens.
3. Execute additional calls to the protocol, exploiting the inconsistent state from step 2 to gain profit.
At a minimum, the following scenarios can be exploited:
• Withdraw tokens, reenter the protocol, and withdraw the same tokens again, effectively double-spending.
• Deposit tokens, reenter the protocol with the placeOrder function, and double-spend the tokens.
This issue is classified as critical severity because it can lead to significant financial loss through double-spending.

## Recommendation
We recommend applying the OpenZeppelin nonReentrant modifier to all public and external mutable functions to prevent reentrancy attacks. Additionally, consider updating the trader's balance before performing the transfer operations.
