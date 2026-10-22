# [M] M-43 | Leverage Doesn't Work When FOT Is Enabled

## Summary
Severity: Medium
Contest weight: 0.1075
Dataset id: 22221
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Pods have a property hasTransferTax which when enabled, a fee-on-transfer is taken from the value to be transferred and the recipient receives less tokens. This is a problem for the [LeverageManager.addLeverage()](https://github.com/GuardianAudits/peapods-2/blob/cebeb47138e5f029cefd698328dfbd33e90fbbea/contracts/lvf/LeverageManager.sol#L128) function because it assumes the whole amount has been received and assigns that amount to LeverageFlashProps.podAmount. Later, when the podAmount is requested from the IndexUtils, the transaction will revert because the LeverageManager contract doesn't have all the tokens.

## Recommendation
Consider the fee on transfer aspect of the pod tokens when adding leverage.
