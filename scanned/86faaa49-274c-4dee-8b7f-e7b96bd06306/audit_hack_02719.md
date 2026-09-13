# [H] Epoch is incremented twice in `initializeEpoch()`when it should only increase by one.

## Summary
Severity: High
Reporter: yixxas
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L246
Type: audit-issue

## Details
# Epoch is incremented twice in `initializeEpoch()`when it should only increase by one.

## Summary
Epoch is wrongly incremented twice in `initalizeEpoch()`. Every function that relies on `_lastEpoch()` to search for the previous result will return a wrong value.

## Vulnerability Detail
`initializeEpoch()` increments `l.epoch` by 1. But in the call to `processDeposits()`, `l.epoch` is incremented again. 

[VaultAdmin.sol#246](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultAdmin.sol#L246)
```solidity
    function initializeEpoch() external onlyKeeper {
        ...
        l.Queue.processDeposits();
        ...
        // increment the epoch id
        l.epoch = l.epoch + 1;
        ...
    }
```

[Queue.sol#L228](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L228)
```solidity
    function processDeposits() external onlyVault {
        ...
        // increment the epoch id
        l.epoch = l.epoch + 1;
    }
```

## Impact
`_lastEpoch()` checks for the previous epoch by subtracting 1. In this case, our epoch id increases sequentially by 2, i.e. 0, 2, 4, 6, 8, 10 ...

[VaultInternal.sol#L694-L700](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L694-L700)
```solidity
    function _lastEpoch(VaultStorage.Layout storage l)
        internal
        view
        returns (uint64)
    {
        return l.epoch > 0 ? l.epoch - 1 : 0;
    }
```
Any function call that relies on `_lastEpoch()` will return a wrong result. For example in `_totalShortAsContracts()`, it tries to query for an epoch that does not exist resulting in a return value of 0 since `shortTokenId = 0`.

[VaultInternal.sol#L131-L135](https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L131-L135)
```solidity
    function _totalShortAsContracts() internal view returns (uint256) {
        VaultStorage.Layout storage l = VaultStorage.layout();
        uint256 shortTokenId = l.options[_lastEpoch(l)].shortTokenId;
        return Pool.balanceOf(address(this), shortTokenId);
    }
```

## Code Snippet

Included code above

## Tool used

Manual Review

## Recommendation

Remove the line `l.epoch = l.epoch + 1` in `processDeposits()`.
