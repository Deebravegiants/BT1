# [M] vePeg#increase_amount and deposit_for incorrectly revert for perpetual locks

## Summary
Severity: Medium
Contest weight: 0.5788
Dataset id: 2743
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function lock_perpetually(uint256 _tokenId) external nonreentrant {
    assert(_isApprovedOrOwner(msg.sender, _tokenId));

    LockedBalance memory currentLock = locked[_tokenId];
    require(currentLock.perpetuallyLocked == false, "Lock is perpetual");
    require(currentLock.end > block.timestamp, "Lock expired");
    require(currentLock.amount > 0, "Nothing is locked");

    uint256 amount = uint256(int256(currentLock.amount));

    LockedBalance memory newLock;
    newLock.end = 0;
    newLock.perpetuallyLocked = true;
    newLock.amount = currentLock.amount;

    perpetuallyLockedBalance += amount;

    _checkpoint(_tokenId, currentLock, newLock);

    locked[_tokenId] = newLock;
}
```

We see above that when a lock is changed to a perpetual lock, that newLock.end is set to 0.

```solidity
function increase_amount(uint256 _tokenId, uint256 _value) external nonreentrant {
    assert(_isApprovedOrOwner(msg.sender, _tokenId));

    LockedBalance memory _locked = locked[_tokenId];

    assert(_value > 0); // dev: need non-zero value
    require(_locked.amount > 0, "No existing lock found");
    require(_locked.end > block.timestamp, "Cannot add to expired lock. Withdraw");

    if (_locked.perpetuallyLocked) {
        perpetuallyLockedBalance += _value;
    }

    _deposit_for(_tokenId, _value, 0, _locked, DepositType.INCREASE_LOCK_AMOUNT);
}
```

The problem is that these tokens can no longer increase in value since 0 is always less than block.timestamp. This leads to issues when users wish to increase the amount or to receive their PEG staking rewards.

## Recommendation
Check should be changed to allow perpetually locked tokens.
