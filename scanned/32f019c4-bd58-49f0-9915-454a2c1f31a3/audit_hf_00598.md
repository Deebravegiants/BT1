# [H] H-06 | Incorrect reservedUsd Logic For Shorts

## Summary
Severity: High
Contest weight: 0.1850
Dataset id: 2097
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The _reservedUsd function calculates the liquidity that must be reserved to ensure suﬃcient funds
are available to pay out traders. The calculation is currently implemented as:
reserved = marketPrice * positions
This approach is valid for long positions, as their payouts increase with rising prices. However, the
logic fails for short positions. For shorts, proﬁts are inversely related to the price. As the price
increases, shorts incur losses, and as the price decreases, shorts generate proﬁts.
The current implementation over-reserves liquidity for shorts when prices rise and, more critically,
under-reserves liquidity when prices fall.

## Recommendation
Consider implementing a separate reservedUsd logic for short positions, taking into consideration
that for shorts, the maximum amount they can proﬁt is up to their cost-basis (e.g. when opening a 1
ETH short at $3000, the maximum proﬁt is $3000).
