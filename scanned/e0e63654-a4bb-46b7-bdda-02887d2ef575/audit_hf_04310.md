# [H] H-07 | Premium Compounding Is Incorrect

## Summary
Severity: High
Contest weight: 0.2009
Dataset id: 21460
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol deploys liquidity to ranges based on a liquidity premium and this premium supposed to be compounding when the difference between the activeTick and the floorTickL increases.
However, due to incorrect usage of the powWad in the getCurrentThreshold function, premium decreases instead of increasing. The reason of this behaviour is the numerator (1e16) in the formula is smaller than 1e18 and it causes result to decrease in every power.
As a result of this, all liquidity managements in sweep and slide will be incorrect, and the maximum liquidity in discovery range will never pass 1.1 * anchor liquidity during these operations.

## Proof of Concept
https://github.com/GuardianAudits/baseline-team-2-pocs/pull/10

## Recommendation
Ensure the formula compounds the premium in a positive way while using the powWad, while being sure to implement the correct test coverage for the liquidity threshold, as this bug was missed by the existing testing coverage.
