# [M] Ended locks can be extended

## Summary
Severity: Medium
Contest weight: 0.4413
Dataset id: 22372
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a lock period ends, it can be extended. If the new extension 'end' is earlier than the current block.timestamp, the user will have a lock that can be unstaked at any time. When the lock period ends, the owner of the expired lock can extend it to set a new lock end that is earlier than the current block.timestamp. By doing so, the lock owner can create a lock that is unstakeable at any time. This is doable because there are no checks in the extendLock function that checks whether the lock is already ended or not.

PoC:
```solidity
function test_ExtendLock_AlreadyEnded() external {
    uint256 amount = 100e18;
    uint256 duration = 5 days;
    _stake(amount, duration, alice, alice);
    // 5 days later, lock is ended for Alice
    skip(5 days + 1);
    (,, uint128 _ends,,) = veTRUF.lockups(alice, 0);
    // Alice's lock is indeed ended
    assertTrue(_ends < block.timestamp, "lock is ended");
    // 36 days passed
    skip(36 days);
    // Alice extends her already finished lock 30 more days
    vm.prank(alice);
    veTRUF.extendLock(0, 30 days);
    (,,_ends,,) = veTRUF.lockups(alice, 0);
    // Alice's lock can be easily unlocked right away
    assertTrue(_ends < block.timestamp, "lock is ended");
    // Alice unstakes her lock, basically alice can unstake her lock anytime she likes
    vm.prank(alice);
    veTRUF.unstake(0);
}
```

The owner of the lock will achieve points that he can unlock anytime. This is clearly a gaming of the system and shouldn't be acceptable behaviour. A locker having a "lock" that can be unstaked anytime will be unfair for the other lockers. Considering this, I'll label this as high.

## Recommendation
Do not let extension of locks that are already ended.
