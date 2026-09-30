# [M] M-23 | Zero Balance Active Collaterals

## Summary
Severity: Medium
Contest weight: 0.0903
Dataset id: 2124
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _depositToAccount function checks the raw amount is not zero, converts raw amount to wad amounts, and then adds collateral to the active collaterals. However, if the collateral's decimal value is higher than 18, wad amount can be zero while the raw amount is not zero. Since the balances are tracked as wad in the protocol, this collateral will still be added to active collaterals even though the wad balance is zero. Similarly, there will be some precision loss when withdrawing collaterals if the decimal value of the collateral is higher than 18.

## Recommendation
Check the wad amount is not zero as well before adding collateral to the active collaterals.
