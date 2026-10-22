# [M] M-4 Incorrect fee calculation

## Summary
Severity: Medium
Contest weight: 0.1148
Dataset id: 10399
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A potential rounding error exists at the TokenLexscrowFactory.sol#L117. The feeDenominatorAdjusted may round down to 0 if a token's decimals are significantly less than 18, leading to the ONE constant being used as _feeDenominatorAdjusted. This results in the fee equating to totalAmount at the TokenLexscrowFactory.sol#L123 Conversely, if decimals exceed 18, feeDenominatorAdjusted does not accurately represent a fraction of totalAmount, resulting in a lower-than-expected _fee. Additionally, tokens with decimals = 0 will encounter a similar issue, as feeDenominatorAdjusted will not reflect the correct proportion of totalAmount.

## Recommendation
We recommend introducing basis points as the denominator for fee calculation and specifying the desired share of _totalAmount as the numerator. The fee calculation would then be: fee = totalAmount * feeshare / BASIS_POINTS; It will lead to increased precision during the fee calculation. We also recommend not using token decimals in the fee calculation.
