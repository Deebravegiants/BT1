# [M] Improved _extendLock() Logic in xLAB

## Summary
Severity: Medium
Contest weight: 0.4597
Dataset id: 12382
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the LayerBank protocol, there is a core xLAB contract that allows users to lock protocol tokens LAB to obtain voting power. While reviewing the lock-extending logic, we notice a logic issue that needs to be addressed. To elaborate, we show below the code snippet of the _extendLock() function. As the name indicates, it is used to extend an existing lock. By design, it requires either the new unlock time is later than previous unlock time or the new voting power is greater than the previous one. However, it comes to our attention that the adjustment of voting power blindly assumes the new voting power is always greater than the previous one. In other words, when the new unlock time is later than previous unlock time, it is possible to have a smaller new voting power, which will revert the current execution. To fix, we may need to accordingly burn the lost voting power that can be computed by deducting the new voting power from the previous one.
```solidity
function _extendLock(address account, uint256 slot, uint256 lockDuration) private nonReentrant whenNotPaused {
    require(lockDuration >= MIN_LOCK_DURATION && lockDuration <= MAX_LOCK_DURATION, "lockDuration is out of range");
    uint256 lockCount = users[account].locks.length;
    require(slot < lockCount, "invalid slot");
    uint256 originalUnlockTime = uint256(users[account].locks[slot].unlockTime);
    uint256 lockedAmount = uint256(users[account].locks[slot].lockedAmount);
    uint256 originalVeAmount = uint256(users[account].locks[slot].veAmount);
    uint256 newUnlockTime = block.timestamp + lockDuration;
    uint256 newVeAmount = calcVeAmount(lockedAmount, lockDuration);
    require(originalUnlockTime < newUnlockTime || originalVeAmount < newVeAmount, "invalid lockDuration");
    users[account].locks[slot].unlockTime = uint48(newUnlockTime);
    users[account].locks[slot].veAmount = newVeAmount;
    _mint(account, newVeAmount.sub(originalVeAmount));
    _updateUserBalanceHistory(account);
    _updateLABDistributorBoostedInfo(account);
    emit ExtendLock(account, slot, newUnlockTime, lockedAmount, originalVeAmount, newVeAmount);
}
```

## Recommendation
Revisit the above _extendLock() function to properly adjust the resulting voting power.
