# [M] TradableSideVault.sol: users can grief sideVaults by spending their funds on LZ messages

## Summary
Severity: Medium
Contest weight: 0.0988
Dataset id: 16156
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Any user can spam function marginAccountDeposit() on a sideVault with an amount of 0 tokens and drain the contract of ether (they would also receive the LZ gas refunded, if any).
They could call this function several times within a single transaction, which would result in a cheap call to grief the vault, but a big cost to the protocol.
This would also prevent other users in the same chain from interacting with the sideVault, not allowing them to make deposits, withdrawals, etc.
Note: Before spamming this function, the griefer would need to run createUserFundingAccount() once, but at a small gas cost.

## Recommendation
Set a minimum deposit amount on side vaults or make the depositor pay for the cost of sending the LayerZero message.
