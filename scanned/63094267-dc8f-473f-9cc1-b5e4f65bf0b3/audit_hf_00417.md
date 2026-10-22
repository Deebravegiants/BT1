# [M] FluidLocker::_getUnlockingPe

## Summary
Severity: Medium
Contest weight: 0.4296
Dataset id: 1825
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
FluidLocker::_getUnlockingPercentage() is calculated as:  
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
As can be seen, it divides before multiplying, leading to precision loss.  
The loss is always ((80*1e18)/Math.sqrt(540*24*3600*1e18))=1712139.4821, so the 0.4821 component is discarded. This corresponds to 0.4821*sqrt(540*24*3600*1e18)*100/1e18=0.00032929935 BPS.  
As this loss is present in every calculation and it will make a 1 BPS different in many instances, it is significant. For example, if the maximum duration is picked, instead of 10000 BPS, it will actually be 9999BPS and 1 BPS goes to the TAX pool. If the user unlocks for example 1e5 USD, this is a 10 USD loss. As it will happen frequently, the loss will accumulate.  
In FluidLocker::388, it divides before multiplying.  
Internal pre-conditions  
None.  
External pre-conditions  
None.  
Attack Path  
1. User calls unlock with vesting period, but due to the precision loss it rounds down and 1 BPS more goes to the tax distribution pool.  
User suffers a 1 BPS loss of funds. For example, 1e5 USD will yield a 10 USD loss.

## Recommendation
Multiply before dividing as it will never overflow.
