# [C] C-09 | Oracle Precision Error Due To Token Decimals

## Summary
Severity: Critical
Contest weight: 0.2450
Dataset id: 22181
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getPrices function aims to return price in 18 decimals, which will be consumed by the aspTKN oracle and ultimately the FraxlendPair contract to determine LTV and borrow amount. The issue lies in _calculateBasePerSpTkn where token decimals are correctly handled up till the calculation of _pairPrice18. As the variable name suggests, this is the price of the LP pair returned in 18 decimals: uint256 _pairPrice18 = (2 * _avgBaseAssetInLp18 * 10 ** ((_clT0Decimals + _clT1Decimals) / 2)) / IERC20(_pair).totalSupply(); However, if either token is not in 18 decimals, e.g. USDC: 6 decimals, then the price returned here will not be in 18 decimals. Assume token0 is 18 decimals and token1 is 6 decimals, the math for decimals works out to be: 18 + ((18 + 6) / 2) - 18 = 12. The incorrect precision affects all downstream calculations and results in a wrong price consumed by FraxlendPair. This ultimately affects LTV calculations which can lead to pairs being drained and users being liquidated unfairly.

## Recommendation
Change the calculations to: uint256 _pairPrice18 = (2 * _avgBaseAssetInLp18 * 10 ** 18 / IERC20(_pair).totalSupply(); Afterwards, remove the _baseTDecimals logic in _spTknBasePrice18.
