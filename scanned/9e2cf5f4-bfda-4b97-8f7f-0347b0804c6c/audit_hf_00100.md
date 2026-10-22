# [M] M-29 | Sandwich Liquidations

## Summary
Severity: Medium
Contest weight: 0.1521
Dataset id: 183
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When liquidations happen a stepwise jump in the value of shares happens. Either the liquidated value will increase the share value or the liquidation reward and/or bad debt will decrease it.
As the init call of deposit/withdraw saves the current balances and calculates the share/asset amt received based on that, users are able to sandwich liquidations to make proﬁt or avoid losses.
Deposit for proﬁt:
• LP sees that a liquidation call will increase the vaults balance
• LP front runs the transaction and initiates a deposit to mint shares based on the old balance
• The liquidation call goes through
• The LP validates the deposit and is in instant proﬁt without price changes
Withdraw to avoid loss:
• LP sees that a liquidation call will decrease the vaults balance (bad debt)
• LP front runs the transaction and initiates a withdraw to burn shares based on the old balance
• The liquidation call goes through
• The LP validates the withdraw and avoided paying for the bad debt and socialized more loss to the other LPs by doing so

## Recommendation
This ﬁnding serves only to document this behavior. Be aware of these potentially unexpected behaviors and how they could be manipulated.
