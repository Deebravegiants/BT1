# [M] Public Writable _unlockIntervalsCount From vestedAmount()

## Summary
Severity: Medium
Contest weight: 0.4607
Dataset id: 13401
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The TokenVesting contract handles the vesting of WOM (Wombat token) for a list of admin-settable beneficiaries. The WOM token transferred to this contract will be locked and the contract will release the token to the beneficiary according to a given vesting schedule. With the vesting schedule, 10% of the total tokens will be unlocked in each interval (6 months). And a total of 10 intervals will be taken to unlock all the tokens. The contract maintains a _unlockIntervalsCount variable for each beneficiary to record the number of unlocked intervals. By design, the _unlockIntervalsCount shall be updated each time the vested tokens have been released to the beneficiary. While examining the logic to update the _unlockIntervalsCount, we notice the variable could be updated publicly from the vestedAmount() routine, which needs to be corrected. To elaborate, we show below the code snippet from the TokenVesting contract. As the name indicates, the vestedAmount() routine is designed to calculate and return the amount of WOM tokens that have already been vested to the given beneficiary by the given timestamp. The vestedAmount() invokes the _vestingSchedule() routine which implements the vesting formula. Especially, when the given timestamp equals the current block.timestamp, the _unlockIntervalsCount will be updated to the latest (line 172). It comes to our attention that the vestedAmount() routine is public accessible. That is to say, everybody could invoke it to update the _unlockIntervalsCount of any beneficiary. As a result, the release of the vested tokens to the beneficiary will be delayed.

```solidity
/**
 * @dev Calculates the amount of WOM tokens that has already vested. Default implementation is a linear vesting curve.
 */
function vestedAmount(address beneficiary, uint256 timestamp) public returns (uint256) {
    uint256 _vestedAmount = _vestingSchedule(
        beneficiary,
        _beneficiaryInfo[beneficiary]._allocationBalance + released(beneficiary),
        uint256(timestamp)
    );
    emit ReleasableAmount(beneficiary, _vestedAmount);
    return _vestedAmount;
}

/**
 * @dev implementation of the vesting formula. This returns the amount vested, as a function of time, for
 * an asset given its total historical allocation.
 * 10% of the Total Number of Tokens Purchased shall unlock every 6 months from the Network Launch,
 * with the Total Number * of Tokens Purchased becoming fully unlocked 5 years from the Network Launch.
 * i.e. 6 months cliff from TGE, 10% unlock at month 6, 10% unlock at month 12, and 10% unlock at month 60
 */
function _vestingSchedule(address beneficiary, uint256 totalAllocation, uint256 timestamp) internal returns (uint256) {
    if (timestamp < start()) return 0;
    else if (timestamp > start() + duration()) return totalAllocation;
    else if (timestamp == uint256(block.timestamp)) {
        uint256 currentInterval = _calculateInterval(timestamp);
        bool isUnlocked = currentInterval > _beneficiaryInfo[beneficiary]._unlockIntervalsCount;
        if (isUnlocked) _beneficiaryInfo[beneficiary]._unlockIntervalsCount = currentInterval;
        return (totalAllocation * currentInterval * 10) / 100;
    } else {
        return ((totalAllocation * _calculateInterval(timestamp) * 10) / 100);
    }
}
```

## Recommendation
Correct the above mentioned logic to update the _unlockIntervalsCount only after the vested tokens have been released to the beneficiary.
