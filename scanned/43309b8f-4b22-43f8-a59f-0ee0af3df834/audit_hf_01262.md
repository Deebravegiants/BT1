# [M] `Minter.sol#_executeInflationRateUpdate

## Summary
Severity: Medium
Contest weight: 0.6435
Dataset id: 5834
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When `Minter.sol#_executeInflationRateUpdate()` is called, if an `_INFLATION_DECAY_PERIOD` has past since `lastInflationDecay`, it will update the InflationRate for all of the gauges.

However, in the current implementation, the rates will be updated first, followed by the rewards being settled using the new rates on the gauges using `inflationManager().checkpointAllGauges()`.

If the `_INFLATION_DECAY_PERIOD` has passed for a long time before `Minter.sol#executeInflationRateUpdate()` is called, the users may lose a significant amount of rewards.

On a side note, `totalAvailableToNow` is updated correctly.

```solidity
function _executeInflationRateUpdate() internal returns (bool) {
    totalAvailableToNow += (currentTotalInflation * (block.timestamp - lastEvent));
    lastEvent = block.timestamp;
    if (block.timestamp >= lastInflationDecay + _INFLATION_DECAY_PERIOD) {
        currentInflationAmountLp = currentInflationAmountLp.scaledMul(annualInflationDecayLp);
        if (initialPeriodEnded) {
            currentInflationAmountKeeper = currentInflationAmountKeeper.scaledMul(
                annualInflationDecayKeeper
            );
            currentInflationAmountAmm = currentInflationAmountAmm.scaledMul(
                annualInflationDecayAmm
            );
        } else {
            currentInflationAmountKeeper =
                initialAnnualInflationRateKeeper /
                _INFLATION_DECAY_PERIOD;

            currentInflationAmountAmm = initialAnnualInflationRateAmm / _INFLATION_DECAY_PERIOD;
            initialPeriodEnded = true;
        }
        currentTotalInflation =
            currentInflationAmountLp +
            currentInflationAmountKeeper +
            currentInflationAmountAmm;
        controller.inflationManager().checkpointAllGauges();
        lastInflationDecay = block.timestamp;
    }
    return true;
}

function checkpointAllGauges() external override returns (bool) {
    uint256 length = _keeperGauges.length();
    for (uint256 i; i < length; i = i.uncheckedInc()) {
        IKeeperGauge(_keeperGauges.valueAt(i)).poolCheckpoint();
    }
    address[] memory stakerVaults = addressProvider.allStakerVaults();
    for (uint256 i; i < stakerVaults.length; i = i.uncheckedInc()) {
        IStakerVault(stakerVaults[i]).poolCheckpoint();
    }

    length = _ammGauges.length();
    for (uint256 i; i < length; i = i.uncheckedInc()) {
        IAmmGauge(_ammGauges.valueAt(i)).poolCheckpoint();
    }
    return true;
}

function poolCheckpoint() public override returns (bool) {
    if (killed) return false;
    uint256 timeElapsed = block.timestamp - uint256(lastUpdated);
    uint256 currentRate = IController(controller).inflationManager().getKeeperRateForPool(pool);
    perPeriodTotalInflation[epoch] += currentRate * timeElapsed;
    lastUpdated = uint48(block.timestamp);
    return true;
}

function getKeeperRateForPool(address pool) external view override returns (uint256) {
    if (minter == address(0)) {
        return 0;
    }
    uint256 keeperInflationRate = Minter(minter).getKeeperInflationRate();
    // After deactivation of weight based dist, KeeperGauge handles the splitting
    if (weightBasedKeeperDistributionDeactivated) return keeperInflationRate;
    if (totalKeeperPoolWeight == 0) return 0;
    bytes32 key = _getKeeperGaugeKey(pool);
    uint256 poolInflationRate = (currentUInts256[key] * keeperInflationRate) /
        totalKeeperPoolWeight;
    return poolInflationRate;
}

function getKeeperInflationRate() external view override returns (uint256) {
    if (lastEvent == 0) return 0;
    return currentInflationAmountKeeper;
}
```

## Proof of Concept
Given:

  * currentInflationAmountAmm: 12,000 Bkd (1000 per month)
  * annualInflationDecayAmm: 50%
  * initialPeriodEnded: true
  * lastInflationDecay: 11 months ago
  * _INFLATION_DECAY_PERIOD: 1 year
  * Alice deposited as the one and only staker in the `AmmGauge` pool;
  * 1 month later;
  * `Minter.sol#_executeInflationRateUpdate()` is called;
  * Alice `claimableRewards()` and received `500` Bkd tokens.

Expected Results:

  * Alice to receive `1000` Bkd tokens as rewards.

Actual Results:

  * Alice received `500` Bkd tokens as rewards.

## Recommendation
Consider moving the call to `checkpointAllGauges()` to before the `currentInflationAmountKeeper` is updated.

```solidity
function _executeInflationRateUpdate() internal returns (bool) {
    totalAvailableToNow += (currentTotalInflation * (block.timestamp - lastEvent));
    lastEvent = block.timestamp;
    if (block.timestamp >= lastInflationDecay + _INFLATION_DECAY_PERIOD) {
        controller.inflationManager().checkpointAllGauges();
        currentInflationAmountLp = currentInflationAmountLp.scaledMul(annualInflationDecayLp);
        if (initialPeriodEnded) {
            currentInflationAmountKeeper = currentInflationAmountKeeper.scaledMul(
                annualInflationDecayKeeper
            );
            currentInflationAmountAmm = currentInflationAmountAmm.scaledMul(
                annualInflationDecayAmm
            );
        } else {
            currentInflationAmountKeeper =
                initialAnnualInflationRateKeeper /
                _INFLATION_DECAY_PERIOD;

            currentInflationAmountAmm = initialAnnualInflationRateAmm / _INFLATION_DECAY_PERIOD;
            initialPeriodEnded = true;
        }
        currentTotalInflation =
            currentInflationAmountLp +
            currentInflationAmountKeeper +
            currentInflationAmountAmm;
        lastInflationDecay = block.timestamp;
    }
    return true;
}
```
This should be medium risk, as should only have a minor impact on users getting less rewards and no over-minting can occur.

The warden has shown how, due to an incorrect order of operations, rates for new rewards can be enacted before the old rewards are distributed, causing a loss of rewards for end users.

There are 2 ways to judge this finding:

  * The system is failing at distributing the proper amount of rewards, hence the finding is of High Severity
  * End users can risk a loss of value if these functions are not called often enough as the difference between the old rates and the new rates will cause a loss of reward for the end users.

Ultimately the impact is a loss of value, further minimized by the fact that anyone can call `poolCheckpoint` as well as `executeInflationRateUpdate` meaning the losses can be minimized.

So from a coding standpoint I believe the bug should be fixed before deployment, but from a impact point of view the impact can be minimized to make “loss of yield” mostly rounding errors.

Given the impact I believe the finding to be of Medium Severity.
