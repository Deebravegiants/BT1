# [M] GLOBAL-1 | Issues With Equity Synthetic Tokens

## Summary
Severity: Medium
Contest weight: 0.0719
Dataset id: 18864
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Equities will potentially be supported for trading, as long as they have a price feed. Potential issues arise in the case of forward stock splits, where the price per share is halved and the number of shares a user owns double. This may require an update to the size in tokens for existing positions or bespoke price logic. Other scenarios include reverse stock splits, mergers and acquisitions, etc.

## Recommendation
Document protocol behavior in such scenarios and carefully monitor markets where such an event is approaching as they are announced in advance.
