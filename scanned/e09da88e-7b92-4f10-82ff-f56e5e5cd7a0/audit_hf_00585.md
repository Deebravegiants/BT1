# [M] Add a timelock to `setPlatformFee`

## Summary
Severity: Medium
Contest weight: 0.0723
Dataset id: 2054
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is a good practice to give time for users to react and adjust to critical changes. A timelock provides more guarantees and reduces the level of trust required, thus decreasing risk for users. It also indicates that the project is legitimate.

Here, no timelock capabilities seem to be used

I believe this impacts multiple users enough to make them want to react / be notified ahead of time.

## Recommendation
Consider adding a timelock to `setPlatformFee()`

This is a good idea. We will consider mitigating this but at the same time it might not be something we will solve
