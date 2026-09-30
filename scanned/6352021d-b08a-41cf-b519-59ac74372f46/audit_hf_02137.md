# [M] Improper Reward Updated in vlEigenpie::cancelUnlock()

## Summary
Severity: Medium
Contest weight: 0.4256
Dataset id: 11989
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Eigenpie protocol has a core vlEigenpie contract that is used to vote-lock Eigenpie tokens. The vote-locked amount is used to calculate the rewards a user may deserve. In the process of examining existing logic to calculate the reward amount, we notice an issue that results from the cancellation of a cool down entry. In the following, we show below the related cancelUnlock() implementation. It has a rather straightforward logic in validating the user input and properly reducing cool down amount being cancelled. However, the user rewards should be calculated before making any adjustment on the cool down amount being cancelled. The reason is that the rewarder.updateFor() (line 306) relies on the user vote-locked amount for reward calculation, which should not be aﬀected by the cool down amount being cancelled.
```solidity
function cancelUnlock(uint256 _slotIndex) external override whenNotPaused nonReentrant {
    _checkIdexInBoundary(msg.sender, _slotIndex);
    UserUnlocking storage slot = userUnlockings[msg.sender][_slotIndex];
    _checkInCoolDown(msg.sender, _slotIndex);
    totalAmountInCoolDown -= slot.amountInCoolDown;
    slot.amountInCoolDown = 0;
    if (address(rewarder) != address(0)) rewarder.updateFor(msg.sender);
    emit ReLock(msg.sender, _slotIndex, slot.amountInCoolDown);
}
```

## Recommendation
Improve the above logic to properly compute the user rewards once a lock in cool down is being cancelled.
