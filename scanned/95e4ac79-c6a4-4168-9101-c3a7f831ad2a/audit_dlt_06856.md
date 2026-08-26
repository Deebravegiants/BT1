# [M] _releaseIntervalSecs is not validated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-vtvl
Published: 2022-09-23
Source: https://github.com/code-423n4/2022-09-vtvl-findings/issues/448
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-09-vtvl/blob/f68b7f3e61dad0d873b5b5a1e8126b839afeab5f/contracts/VTVLVesting.sol#L245-L304


# Vulnerability details


## Impact
VTVLVesting.sol has `_createClaimUnchecked` function to create the claims internally while validating parameters with the users' allocations.
However, `_releaseIntervalSecs` is not validated comparing to user's  `_linearVestAmount` and `_startTimestamp` `_endTimestamp`.
Theoratically, `_linearVestAmount` should be equal to `((_endTimestamp - _startTimestamp) * _releaseIntervalSecs)` so the `_releaseIntervalSecs` = `_linearVestAmount / ((_endTimestamp - _startTimestamp)`
But this check was never done.

If the `_releaseIntervalSecs` is validated either to a higher or to a lower amount, it will create unfair distributions amongst the users during withdrawals due to being higher/lower than it should be. And also it may end up with the last withdrawals can be reverted due to the calculation board not matching.

## Proof of Concept

```solidity
    function _createClaimUnchecked(
            address _recipient, 
            uint40 _startTimestamp, 
            uint40 _endTimestamp, 
            uint40 _cliffReleaseTimestamp, 
            uint40 _releaseIntervalSecs, 
            uint112 _linearVestAmount, 
            uint112 _cliffAmount
                ) private  hasNoClaim(_recipient) {


        require(_recipient != address(0), "INVALID_ADDRESS");
        require(_linearVestAmount + _cliffAmount > 0, "INVALID_VESTED_AMOUNT"); // Actually only one of linearvested/cliff amount must be 0, not necessarily both
        require(_startTimestamp > 0, "INVALID_START_TIMESTAMP");
        // Do we need to check whether _startTimestamp is greater than the current block.timestamp? 
        // Or do we allow schedules that started in the past? 
        // -> Conclusion: we want to allow this, for founders that might have forgotten to add some users, or to avoid issues with transactions not going through because of discoordination between block.timestamp and sender's local time
        // require(_endTimestamp > 0, "_endTimestamp must be valid"); // not necessary because of the next condition (transitively)
        require(_startTimestamp < _endTimestamp, "INVALID_END_TIMESTAMP"); // _endTimestamp must be after _startTimestamp
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-09-vtvl-findings/issues/448_
