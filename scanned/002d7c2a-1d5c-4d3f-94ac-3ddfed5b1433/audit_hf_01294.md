# [H] riskPoolBalance is overwritten

## Summary
Severity: High
Contest weight: 0.0975
Dataset id: 6103
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
riskPoolBalance is reassigned instead of adding it to the new amount: pot.riskPoolBalance = riskPoolBalance; riskPoolBalance currently is locked but the intention is to reuse it in later rounds if a player doesn't join. In that case, the aggregated risk pool won't be used since it only stores the latest value.

## Recommendation
Add the new value instead of overwriting; pot.riskPoolBalance += riskPoolBalance;
