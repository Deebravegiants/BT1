# [C] DPCU-2 | LimitDecrease Gamed With EmptyPosition Error

## Summary
Severity: Critical
Contest weight: 0.2045
Dataset id: 18167
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Removing all of the collateral from a position will result in the EmptyPosition error, which will be retried for LimitDecrease orders. An attacker can leverage this by creating a LimitDecrease order that initially only reduces their position.sizeInUsd by half, but reduces their collateral to 0. The LimitDecrease will continue to result in the EmptyPosition error until the attacker creates a MarketDecrease order that reduces the size of their position by half. Now when the original LimitDecrease is executed, it will close the position and no longer revert with the EmptyPosition error. A malicious trader can leverage this to make a risk-free trade with their LimitDecrease.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/DPCU_2.ts

## Recommendation
Revert with the InsufficientCollateral error, which is not retried, in the case where values.remainingCollateralAmount is 0.
