# [H] H-05 | Unauthorized Position Creation

## Summary
Severity: High
Contest weight: 0.2681
Dataset id: 2095
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The permissionless OrderBook.depositCollateral() function allows anyone to deposit collateral for a
given positionId. If the position account doesn't exist, it will be created.
As we can see from LibCodec, the ﬁrst 20 bytes of the positionId are the address of its owner and
the last 12 bytes show if the position supports one or many markets. If the last 12 bytes are 0, the
account is a multimarket one, otherwise it supports only one market.
Each address can have up to MAX_POSITION_ACCOUNT_PER_TRADER different position accounts
(currently set to 64). A malicious user can call deposit 64 times and add 1 wei of collateral to any
positionId, which means they can create 64 single market accounts for a given address.
In result, the victim address will have to either use only single market accounts or change their
address. However, the attack can be executed for their new address again.
This can also be detrimental for smart contracts if they have used only single market accounts, but
try to create a multimarket one - the contract will probably experience DOS.

## Recommendation
Add one of the following restrictions:
• depositCollateral is permissionless only if the positionId already exists.
• depositCollateral can be called only for positions owned by the caller.
