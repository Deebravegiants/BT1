# [M] M-04 | probabilityDenominator Increased If No Swap

## Summary
Severity: Medium
Contest weight: 0.0710
Dataset id: 22058
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the reheat function, the probability denominator is incremented with each successful hit to make future hits less likely. However, when reserveSize = 0, no swap occurs despite the successful hit, but the probability denominator is still incremented. This reduces the likelihood of true hits (where actual swaps occur) since hits that result in no swaps still affect the probability, making legitimate hits less frequent.

## Recommendation
Consider incrementing the probability denominator only if a swap occurs.
