# [M] Every LRT should have seperate liquidateThresholdPect

## Summary
Severity: Medium
Contest weight: 0.0978
Dataset id: 8738
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, the protocol uses the same liquidateThresholdPect for all supported LRTs. Users are allowed to mint cvETH up to the maxLTV percentage, and liquidateThresholdPect serves as the buffer percentage beyond which a user's position will be liquidated.
If a specific asset is considered more risky (volatile), the protocol sets a lower maxLTV for it. However, the liquidateThresholdPect should also vary based on the LRT’s volatility.
For example:
If eETH is considered more volatile and only 50% maxLTV is allowed, setting liquidateThresholdPect to just 2% could make users' positions too easily liquidatable.

## Recommendation
Allow different liquidation threshold percentages for each LRT based on its volatility.
