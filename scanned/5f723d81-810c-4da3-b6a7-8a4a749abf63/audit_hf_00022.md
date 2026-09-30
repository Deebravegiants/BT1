# [M] DIEM-8 | averageEntry Always Rounds Up

## Summary
Severity: Medium
Contest weight: 0.0555
Dataset id: 98
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _openTrade function, when the averageEntry is computed with an earlier trade, mulDivUp is used. However, a higher averageEntry is more beneficial for contracts where isBuy == false. Malicious traders are therefore able to increase their resulting PNL by splitting their trades up and abusing the round up behavior.

## Recommendation
Round up for isBuy == true and round down for isBuy == false.
