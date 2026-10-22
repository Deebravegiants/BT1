# [H] Wrong total supply amount leads to problems with the fees

## Summary
Severity: High
Contest weight: 0.2078
Dataset id: 7623
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
From the documentation and the tokenomics we can see that the total supply should be 10 billion tokens.
However, the amount in the code is 100 million which is much less.
uint256 private _tTotal = 100_000_000 * 10 ** 9;
This leads to problems with the fess, the max amount transactions and all of the limitations of the project.
For example, the _maxTxAmount is required to be more than 10 million:
function setMaxTxAmount(uint256 maxTxAmount) external onlyOwner {
require(maxTxAmount > 10_000_000, "Max Tx Amount cannot be less than
10m");
_maxTxAmount = maxTxAmount * 10 ** 9;
If the total supply is 100 million then that is 10% of the total supply at minimum. If a transaction with such
amount actually happens this will have a huge impact on the price of the token and will lead to massive
slippage.

## Recommendation
Change the total supply to the correct amount.
- uint256 private _tTotal = 100_000_000 * 10 ** 9;
+ uint256 private _tTotal = 10_000_000_000 * 10 ** 9;
