# [M] `confirmBaseInterestAllocator

## Summary
Severity: Medium
Contest weight: 0.6955
Dataset id: 21178
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function confirmBaseInterestAllocator(address _newBaseInterestAllocator) external {
    address cachedAllocator = getBaseInterestAllocator;
    if (cachedAllocator != address(0)) {
        if (getPendingBaseInterestAllocatorSetTime + UPDATE_WAITING_TIME > block.timestamp) {
            revert TooSoonError();
        }
        if (getPendingBaseInterestAllocator != _newBaseInterestAllocator) {
            revert InvalidInputError();
        }
        IBaseInterestAllocator(cachedAllocator).transferAll();
        asset.approve(cachedAllocator, 0);
    }
    asset.approve(_newBaseInterestAllocator, type(uint256).max);

    getBaseInterestAllocator = _newBaseInterestAllocator;
    getPendingBaseInterestAllocator = address(0);
    getPendingBaseInterestAllocatorSetTime = type(uint256).max;

    emit BaseInterestAllocatorSet(_newBaseInterestAllocator);
}
```

The current logic is:

1. Take all the balance of the old `BaseInterestAllocator` and put it in `Pool`.
2. Change `getBaseInterestAllocator` to the new `BaseInterestAllocator`.

If the old `BaseInterestAllocator` already has a large balance, the balance of the Pool will increase dramatically. Subsequent users executing `reallocate()` will get a big bonus `getReallocationBonus`.

```solidity
function reallocate() external nonReentrant returns (uint256) {
    (uint256 currentBalance, uint256 targetIdle) = _reallocate();
    uint256 delta = currentBalance > targetIdle ? currentBalance - targetIdle : targetIdle - currentBalance;
    uint256 shares = delta.mulDivDown(totalSupply * getReallocationBonus, totalAssets() * _BPS);

    _mint(msg.sender, shares);

    emit Reallocated(delta, shares);

    return shares;
}
```

Assuming old `BaseInterestAllocator` balance: 1 M: `shares = 1 M * (1 - optimalIdleRange.mid) * totalSupply * getReallocationBonus / totalAssets()`

## Recommendation
```solidity
function confirmBaseInterestAllocator(address _newBaseInterestAllocator) external {
    address cachedAllocator = getBaseInterestAllocator;
    if (cachedAllocator != address(0)) {
        if (getPendingBaseInterestAllocatorSetTime + UPDATE_WAITING_TIME > block.timestamp) {
            revert TooSoonError();
        }
        if (getPendingBaseInterestAllocator != _newBaseInterestAllocator) {
            revert InvalidInputError();
        }
        IBaseInterestAllocator(cachedAllocator).transferAll();
        asset.approve(cachedAllocator, 0);
    }
    asset.approve(_newBaseInterestAllocator, type(uint256).max);

    getBaseInterestAllocator = _newBaseInterestAllocator;
    getPendingBaseInterestAllocator = address(0);
    getPendingBaseInterestAllocatorSetTime = type(uint256).max;
    if (cachedAllocator != address(0)) {
        _reallocate();
    }
    emit BaseInterestAllocatorSet(_newBaseInterestAllocator);
}
```
