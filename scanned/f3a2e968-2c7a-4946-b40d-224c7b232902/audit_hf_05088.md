# [M] Rewards supplied to a gauge, prior to its first

## Summary
Severity: Medium
Contest weight: 0.4047
Dataset id: 23109
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Rewards supplied to a gauge, prior to its first depositor will be permanently lost. Every week, gauges receive rewards based on their pool weight, within the Voter contract.
```solidity
function distribute(address _gauge) public lock {
    IMinter(minter).update_period();
    _updateFor(_gauge); // should set claimable to 0 if killed
    uint _claimable = claimable[_gauge];
    if (_claimable > IGauge(_gauge).left(base) && _claimable / DURATION > 0) {
        claimable[_gauge] = 0;
        if((_claimable * 1e18) / currentEpochRewardAmount > minShareForActiveGauge) {
            activeGaugeNumber += 1;
        }
        IGauge(_gauge).notifyRewardAmount(base, _claimable);
        emit DistributeReward(msg.sender, _gauge, _claimable);
    }
}
```
The problem is that any rewards sent to the gauge prior to its first depositor will remain permanently stuck. Given that rewards are sent automatically, the likelihood of such occurrence is significantly higher. Loss of funds.

## Recommendation
Revert in case current supply is 0.
