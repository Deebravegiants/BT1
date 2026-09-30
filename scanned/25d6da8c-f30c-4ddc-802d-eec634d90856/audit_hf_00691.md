# [M] M-12 | Tokens Are Tradable When The LT Is Liquidatable

## Summary
Severity: Medium
Contest weight: 0.0802
Dataset id: 2242
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• The docs state out that LTs are supposed to be used in third-party DeFi protocols and they are transferable.
• The mintFor function checks that the LT's position is not liquidatable and active, to make sure that a user does not enter the system and likely loses their invested funds right after.
The _update function executed during transfers when users acquire LTs on third-party protocols does not perform these checks. Therefore users could end up acquiring worthless LTs.

## Recommendation
Consider reverting in the _update function if the LT's position is liquidatable or no longer active.
