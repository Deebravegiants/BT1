# [M] M-04 | GLV Used To Exit Illiquid Markets

## Summary
Severity: Medium
Contest weight: 0.0785
Dataset id: 21908
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
GLV allows users to essentially swap between GM markets with no fees by triggering a GLV deposit of GM market A and triggering a GLV withdrawal of GM market B. An actor holding GM market A can observe that GM market A is locked due to pnlToPoolRatio validations or reserves validations and use GLV to exit their GM A tokens into GM B tokens. This will come at the expense of all other GLV holders, who are now left with the illiquid GM A tokens.

## Recommendation
Consider applying an additional fee to GLV withdrawals to disincentivize this or disallowing GLV deposits when the underlying GM market is illiquid.
