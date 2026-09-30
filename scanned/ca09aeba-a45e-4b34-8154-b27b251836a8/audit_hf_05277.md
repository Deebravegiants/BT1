# [H] LockUpManager::_unlockTokens returns if lockUpTime == 0

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23507
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: LockUpManager::_unlockTokens returns if lockUpTime == 0:
```solidity
function _unlockTokens(
    address holder,
    uint256 amount,
    bool disregardTime
) internal {
    LockUpStorage storage $ = _getLockUpStorage();
    uint32 lockUpTime = $._lockUpTime;
    // @audit returns if `lockUpTime == 0`
    if (lockUpTime == 0 || amount == 0) return;
    // ... (remaining logic)
}
```
Impact: Tokens that were locked when lockUpTime > 0 will be impossible to unlock if lockUpTime is subsequently set to zero. Initially this won't cause any problems and users will be able to transfer tokens as normal, but if lockUpTime is changed to be greater than zero it will start to cause accounting-related problems as one of the protocol invariants is that the amount of tokens a user has locked should be <= to the token balance of the user. This invariant would be violated since the lockups would still be present but the user could have transferred their tokens, causing underflow reverts in transfers when determine unlocked balance: `uint256 unlockedBalanceToSend = balance - getTokensLocked(sender);`

## Recommendation
Recommended Mitigation: Even if lockUpTime == 0, proceed through to the for loop iterating over all token locks to unlock them. This maintains the protocol invariant that the amount of tokens a user has locked is <= the user's token balance.
