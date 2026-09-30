# [M] GG-5 | Dividend Sniping

## Summary
Severity: Medium
Contest weight: 0.0520
Dataset id: 4053
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because it is possible to publicly see transactions that are sending value to distributeDividends, bots can frontrun the distribution. This way addresses may sandwich a deposit and withdrawal around a distribution in order to unfairly accumulate dividends while never effectively holding the token.

## Recommendation
Introduce a warmup period, or require locking for dividends.
