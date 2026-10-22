# [H] Attackers can claim deposits to vaults if users specify the router as receiver and don't withdraw shares after

## Summary
Severity: High
Contest weight: 0.1626
Dataset id: 8214
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BaseRouter checks if the initial balance of the tokens interacted with is the same as the end balance. However, for vaults, it only checks the balance of the underlying asset, not the shares themselves. Thus, for example, when a user makes a deposit action and specifies the BaseRouter as the receiver, but does not do any further action, the shares will be locked in the BaseRouter. Then, an attacker can call the withdrawal action of the BaseRouter and redeem these shares for any receiver.

## Proof of Concept
no poc/POCAttackerStealsUser.t.sol#L40/POCAttackerStealsUser.t.sol#L40

## Recommendation
Add to the tokensToCheck array the address of the vault itself (its shares).
