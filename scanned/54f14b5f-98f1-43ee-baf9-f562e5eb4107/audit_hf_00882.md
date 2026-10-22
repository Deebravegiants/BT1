# [M] InfraredCollateralVault::rebalance()

## Summary
Severity: Medium
Contest weight: 0.1377
Dataset id: 2638
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
InfraredCollateralVault::rebalance() decreases a currency balance for the asset(). However, the decrease in the sent currency is not capped to the current unlocked balance, allowing balance allocated to future emissions to be used. An attacker can force this by withdrawing some funds in the currency sent used to rebalance, before the admin rebalances, in order to make the rebalance send too many sent currency and DoS the protocol. In InfraredCollateralVault:180, rebalance(), there is no cap in the sent currency to rebalance. Internal Pre-conditions None. External Pre-conditions None. Attack Path 1. Attacker frontruns admin rebalance with withdraw() call in the token that is going to be rebalanced by an admin. 2. The rebalance call withdraws too many token, leading to an underflow when calculating the unlocked balance in totalAssets(), 1, 2, 3 DoSing the protocol. All protocol functions are DoSed due to the underflow above.

## Recommendation
Check if the amount to rebalance is smaller than the current unlocked balance.
