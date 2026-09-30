# [M] No liquidation incentives if the discount interval has passed

## Summary
Severity: Medium
Contest weight: 0.1054
Dataset id: 9809
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position is liquidated, a discount factor is calculated based on the time that has passed since the start of the auction. The auction follows a Dutch auction design, where the discount factor decreases linearly to zero if a configured period, DiscountInterval has passed. However, it is better to keep a non-zero discount even if the period has passed, which would ensure that liquidators have an incentive to liquidate underwater positions in the system. Otherwise, without being liquidated, the position's debt could increase over time and potentially become bad debt, which puts the protocol at risk of insolvency.

## Recommendation
Consider defining a variable as the minimum discount factor, which can be configurable by the controller or admin, and setting the discount variable to this value when a specific interval has passed.
