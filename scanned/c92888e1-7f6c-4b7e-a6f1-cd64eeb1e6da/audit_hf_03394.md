# [M] EDPU-1 | Users Are Negatively Affected By The Price Spread

## Summary
Severity: Medium
Contest weight: 0.0791
Dataset id: 18502
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the positiveImpactAmount is calculated during a deposit, the _params.priceImpactUsd is
divided by the tokenPrice.max to be converted into an outToken amount. However the token amount
is converted back to a USD amount when incrementing the mintAmount,
positiveImpactAmount.toUint256() * _params.tokenOutPrice.min.
This means that users are negatively impacted by the price spread because they receive less
positive impact than they otherwise would have.

## Recommendation
Multiply the positiveImpactAmount by the _params.tokenOutPrice.max so that users are not
negatively impacted by the price spread.
