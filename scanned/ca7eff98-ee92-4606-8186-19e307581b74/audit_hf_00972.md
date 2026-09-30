# [H] The asset valuation for derived assets is broken

## Summary
Severity: High
Contest weight: 0.7280
Dataset id: 3036
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Derived assets are incorrectly valued which among other things can lead to premature
liquidations.

An account's numeraire is the unit in which all assets and liabilities of the Account are
measured. The numeraire can be a derived asset and doesn't have to be a simple ERC20.
The numeraire plays a significant part in calculating the liquidation value.
There are two possible ways the liquidation value is calculated, starting from:
• Registry.getLiquidationValue()
• AccountV1.startLiquidation()
In the Registry's case, the downstream call to get the numeraire value is:

```solidity

## Recommendation
```solidity
