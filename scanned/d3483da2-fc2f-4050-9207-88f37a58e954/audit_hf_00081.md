# [M] M-21 | Extracting From Rebalancer Bonus

## Summary
Severity: Medium
Contest weight: 0.1531
Dataset id: 157
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Rebalance mechanism is crucial for holding the protocol in balance, hence the users are incentivized to deposit funds to rebalancer (no fee for position opening, 80% of the remaining collateral from the liquidations will be distributed etc.)
However this mechanism can be gamed such that a user can sandwich a liquidation call to extract value from rebalancer bonus without a need for locking value in rebalancer more than a couple minutes.
Here are the steps to perform the attack:
1- Deposit into the rebalancer near liquidation and into the vault to increase imbalance.
2- Frontrun any user's liquidation attempt and perform the following in one transaction:
2.1- Validate rebalancer deposit
2.2- Liquidate (Which will create a rebalancer position)
2.3- Initiate a withdrawal from vault so that it will be possible to withdraw from rebalancer.
2.4- Initiate rebalancer close.
3- Wait 24 seconds (delay) and validate the withdrawal from vault and rebalancer close.
Result: Profit from bonus in rebalancer + pnl from trades in vault.

## Recommendation
Prevent position closing from the rebalancer for some time after deposits so that there won't be a risk-free profit opportunity with the specified attack anymore.
