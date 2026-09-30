# [C] LGR-1 | Duplicated insuranceTransferAmount

## Summary
Severity: Critical
Contest weight: 0.1641
Dataset id: 19336
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the executeSettlement function, if the settlement.insuranceTransferAmount amount is nonzero it is added to both the insuranceFund.balances and the account.balances therefore duplicating the settlement.insuranceTransferAmount across these two accounts. The validation on the insuranceTransferAmount indicates that the settlement.insuranceTransferAmount should be deducted from the insuranceFund.balances and added or “transferred” to the account.balances.

## Recommendation
Modify the following lines:
insuranceFund.balances[settlement.settledAssetHash] += settlement.insuranceTransferAmount;
account.balances[settlement.settledAssetHash] += settlement.insuranceTransferAmount;
Such that the balance is transferred rather than duplicated:
insuranceFund.balances[settlement.settledAssetHash] -= settlement.insuranceTransferAmount;
account.balances[settlement.settledAssetHash] += settlement.insuranceTransferAmount;
