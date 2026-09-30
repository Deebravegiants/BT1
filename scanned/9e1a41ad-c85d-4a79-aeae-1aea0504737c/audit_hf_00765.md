# [C] C-02 | Position Liquidity Unaltered

## Summary
Severity: Critical
Contest weight: 0.1496
Dataset id: 2385
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the cancelOrder function there is no logic to reduce the totalLiquidity amount stored on the position such as in the _updateUserPosition function.
As a result, as soon as one user cancels an order in a given range, all other users will be unable to be executed and swaps in the pool will be DoS’d past that tick as the callback reverts due to attempting to burn more liquidity than exists in the position.

## Proof of Concept
https://github.com/GuardianOrg/univ4-limit-order-hook-team2/pull/1

## Recommendation
Introduce logic into the cancelOrder function such that the totalLiquidity of the position is reduced in line with the amount that was burnt for the user.
