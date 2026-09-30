# [M] MKTU-2 | Negative Pool Value DoS

## Summary
Severity: Medium
Contest weight: 0.0839
Dataset id: 18863
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the result.poolValue is negative it is impossible to deposit into a market to make it useable again. There can be leftover index tokens in the position impact pool which are subtracted from the pool value. Consequently, it is possible to achieve a state where the supply of market tokens is 0, but the pool value is negative. Such a scenario would shut down the market, preventing inﬂow of any deposits and further usage. However, it is important to note that such a scenario would be rare.

## Recommendation
Clearly document that such a scenario can occur, and monitor impact factors to help prevent such a situation from arising.
