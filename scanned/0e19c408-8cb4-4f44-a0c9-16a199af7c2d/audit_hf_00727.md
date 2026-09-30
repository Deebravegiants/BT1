# [H] H-08 | Large Orders Can Exceed minimumCredit

## Summary
Severity: High
Contest weight: 0.1475
Dataset id: 2278
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the validateTrade function the minimumCredit is validated before accounting for the position’s size in the market. Therefore positions which push the market in the minimumCredit, potentially by a large amount, are allowed to be settled. Neither Traders nor LPs should be able to put the market in a state where the minimumCredit is exceeded, therefore the minimumCredit validation should be performed after taking the position’s sizeDelta into account for the market.

## Recommendation
Validate the minimumCredit after the market size has been updated in settleOrder. Consider leaving the current minimumCredit validation where it is now in order to offer some preemptive validation for order commitments.
