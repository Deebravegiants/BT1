# [M] It should use timelock on `allowedAsset` and `allowedCollection`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-bullvbear
Published: 2022-11-21
Source: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/131
Type: sherlock-finding

## Details
GimelSec

medium

# It should use timelock on `allowedAsset` and `allowedCollection`

## Summary

It's a centralized issue in the protocol. The owner can adjust `allowedAsset` and `allowedCollection` anytime and delete some assets/collections immediately to deny the match of some orders.

## Vulnerability Detail

The owner can call `setAllowedCollection` and `setAllowedAsset` to set `allowedAsset` and `allowedCollection`. However it doesn't have timelock, the owner can set them anytime to block users to call `matchOrder()` because `checkIsValidOrder()` will be reverted on [L754](https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L754) and [L757](https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L757).

## Impact

Users will be unable to match orders due to the malicious/compromised owner.

## Code Snippet

https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L816-L836

## Tool used

Manual Review

## Recommendation

Use timelock to prevent centralized issues. For example:
```solidity
    function setAllowedAsset(address asset, bool allowed) public onlyOwner {
        pendingAsset = asset;
        pendingAllowed = allowed;
        setAllowedAssetTimestamp = block.timestamp;

        emit PendingAllowAsset(asset, allowed);
    }

```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/131_
