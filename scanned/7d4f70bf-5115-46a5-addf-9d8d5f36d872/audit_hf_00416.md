# [H] FluidLocker::_getUnlockingPe

## Summary
Severity: High
Contest weight: 0.7818
Dataset id: 1822
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
FluidLocker::_getUnlockingPercentage() calculates the amount to unlock when unvesting via the FluidLocker. It incorrectly uses 540 instead of 540days, yielding a massive error such that the unlocking percentage will be much bigger than 10_000 and underflow.  
```solidity
function _getUnlockingPercentage(uint128 unlockPeriod) internal pure returns (uint256 unlockingPercentageBP) {
    unlockingPercentageBP = (
        _PERCENT_TO_BP
        * (
            ((80 * _SCALER) / Math.sqrt(540 * _SCALER)) *
            (Math.sqrt(unlockPeriod * _SCALER) / _SCALER)
            + 20 * _SCALER
        )
    ) / _SCALER;
}
```
In FluidLocker:388 it uses 540 instead of 540days.  
Internal pre-conditions  
None.  
External pre-conditions  
None.  
Attack Path  
1. User unlocks their Fluid from the FluidLocker, but it reverts because of the mentioned underflow. The funds within the locker will be stuck unless the user instantly unlocks and takes a 80% penalty.  
User is forced to take a 80% penalty or have the funds stuck.

## Proof of Concept
The calculation is presented in the summary. Essentially, as 540 is used in the denominator, much smaller than the correct 540days (which is the maximum unlock period, when the percentage becomes 100%), the value will be much bigger than 10_000.  
As the unlocking percentage is bigger than 10_000, the unlock flow rate  
```solidity
unlockFlowRate = (globalFlowRate * int256(_getUnlockingPercentage(unlockPeriod))).toInt96()
    / int256(_BP_DENOMINATOR).toInt96();
```
will be bigger than the global flow rate, so it reverts when calculating the tax flow rate taxFlowRate=globalFlowRate-unlockFlowRate;.

## Recommendation
Use 540days instead of 540.
