# [M] M-23 | Blocked Queue Due To Non-Validatable Action

## Summary
Severity: Medium
Contest weight: 0.1271
Dataset id: 159
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users should be able to validate open positions as long as the price is above their liquidation price.
In case of sudden price drops, user's validation price could be below their liquidation price, causing a revert on the leverage calculation.
As the validation price is a fixed Pyth update price during a certain time interval, it should always use the same exact update data. Once this blocked action becomes actionable, any user creating a new action should also pass a previousActionsData param, to validate the next actionable action in queue.
Therefore, the blocked action will now DoS new protocol actions for 5 minutes, from lowLatencyValidatorDeadline to lowLatencyDelay. The admins will need to wait lowLatencyValidatorDeadline + 1 hours in order to unblock this action and the user will lose the security deposit.

## Recommendation
Early return if the validation price is below the liquidation price, to signal a liquidatable state: data_.isLiquidationPending = true;
