# [H] Partial liquidations allow position management blocking and liquidation prevention due to queue mechanism implementation

## Summary
Severity: High
Contest weight: 0.3374
Dataset id: 9808
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LiquidOps protocol allows partial liquidations where only a portion of a loan is liquidated. When a liquidation is initiated, the target user is added to a LiquidationQueue to prevent duplicate liquidations: -- Add the target to the liquidation queue to lock further liquidations table.insert(LiquidationQueue, target) The user remains in this queue until the liquidation is complete, at which point they are removed: -- Remove target from liquidation queue to allow further liquidations LiquidationQueue = utils.filter( function (v) return v ~= target end, LiquidationQueue ) While a user is in the LiquidationQueue, they are prevented from performing certain operations, as many protocol actions check if the user is queued: -- check-queue handler -- the user is queued if they're either in the collateral -- or the liquidation queues return msg.reply({ ["In-Queue"] = json.encode( utils.includes(user, CollateralQueue) or utils.includes(user, LiquidationQueue) ) }) Due to lack of minimum liquidation size requirements, this implementation allows for two attack vectors: 1. An attacker could liquidate a minimal amount of a user's position to forcefully add them to the queue, temporarily preventing them from performing critical actions such as repaying loans or managing collateral. 2. Users at risk of liquidation could create multiple accounts to perform minimal self-liquidations (as direct self-liquidation is not allowed from the protocol), effectively preventing other liquidators from capturing the full liquidation incentives and potentially preventing the liquidation of undercollateralized positions.

## Recommendation
Implement a minimum liquidation threshold as a percentage of the total outstanding loan (e.g., 20%) to make these attacks economically unfeasible. While this does not fully mitigate the issue, it makes the attack much more expensive to perform.
