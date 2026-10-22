# [M] Non-Lockable User Withdrawals in VotingEscrowV2

## Summary
Severity: Medium
Contest weight: 0.4126
Dataset id: 13282
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.5, the Tranchess protocol has an updated VotingEscrowV2 contract. The new update brings the ManagedPausable functionalities to pause exported functions, such as createLock(), increaseAmount(), and increaseUnlockTime(). In the following, we show below another affected withdraw() function, which can also be paused with the addition of the new whenNotPaused modifier. Considering the non-custodial design of the Tranchess protocol, we suggest to remove this modifier from the withdraw() function. In other words, the unlocked funds should be releasable back to the user when the lockup time is over.
```solidity
function withdraw()
external
nonReentrant
whenNotPaused {
    LockedBalance memory lockedBalance = locked[msg.sender];
    require(block.timestamp >= lockedBalance.unlockTime, "The lock is not expired");
    uint256 amount = uint256(lockedBalance.amount);
    lockedBalance.unlockTime = 0;
    lockedBalance.amount = 0;
    locked[msg.sender] = lockedBalance;
    IERC20(token).safeTransfer(msg.sender, amount);
    emit Withdrawn(msg.sender, amount);
}
```

## Recommendation
Remove the whenNotPaused modifier from the above withdraw() function.
