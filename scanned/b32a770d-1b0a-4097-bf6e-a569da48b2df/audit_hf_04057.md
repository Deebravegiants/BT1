# [H] VF-1 | Wrong GMI Conversion Calculation

## Summary
Severity: High
Contest weight: 0.5560
Dataset id: 20509
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GMX fees get added on top of the base withdraw/deposit fees if they are enabled through shouldUseGmxFee. In the case of a withdrawal, those fees are calculated based on the withdrawal size in GMI.

The issue arises due to the following line, which gets used to turn the withdrawal size into GMI, which then gets turned into corresponding GM token amounts:
```solidity
gmi.sharesToMarketTokens(size * gmi.pps(prices) / 10 ** ERC20(asset).decimals(), prices)
```
The formula used for the calculation does not convert a USD notional amount into GMI, but quite the opposite. This will always lead to a much larger fee due to the skewed GM token amounts, thus losing users' funds through excessive fees.

## Recommendation
Convert size into a USD notional value and use a formula for converting USD into GMI: size * 1e18 / gmi.pps(prices).
