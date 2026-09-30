# [M] swapToGNS doesn't add any slippage protec-

## Summary
Severity: Medium
Contest weight: 0.0581
Dataset id: 19773
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The uniswapV3Swap call doesn't implement any kind of slippage protection allowing it to be sandwich attacked.
#L195-L196
We can see here that it calls the swap with not slippage protection at all. This allows the caller to sandwich attack the trade and steal all the DAI being swapped.
DAI being swapped can be stolen via sandwich attack

## Recommendation
Implement a percentage slippage protection using the price of GNS
