# [H] `YieldWUSDStaking.repay

## Summary
Severity: High
Contest weight: 0.7709
Dataset id: 22312
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Code reference: [YieldWUSDStaking.sol#L468](https://github.com/code-423n4/2024-12-benddao/blob/489f8dd0f8e86e5a7550cc6b81f9edfe79efbf4e/src/yield/wusd/YieldWUSDStaking.sol#L468)

In `YieldWUSDStaking.repay()`, we will calculate the amount that needs to be refunded to the user `remainAmount`:

```solidity
function _repay(uint32 poolId, address nft, uint256 tokenId) internal virtual {
    ...
    // compute fine value
    if (vars.remainAmount >= sd.unstakeFine) {
        vars.remainAmount = vars.remainAmount - sd.unstakeFine;
    } else {
        vars.extraAmount = vars.extraAmount + (sd.unstakeFine - vars.remainAmount);
        // missing clear  vars.remainAmount = 0
    }

    sd.remainYieldAmount = vars.remainAmount;
    ...

    // send remain funds to owner
    if (sd.remainYieldAmount > 0) {
        underlyingAsset.safeTransfer(vars.nftOwner, sd.remainYieldAmount);
        sd.remainYieldAmount = 0;
    }
```

The problem is that when use call `repay()`, if `vars.remainAmount < sd.unstakeFine`, it doesn’t clear `vars.remainAmount` to 0, which results in a refund to the user, which should be treated as `unstakeFine`.

For example: unstakeFine = 10 , remainAmount = 5

As currently calculated

1. extraAmount = (unstakeFine - remainAmount ) = 10 - 5 = 5
2. remainYieldAmount = 5 =====> ( should 0)

## Recommendation
```solidity
function _repay(uint32 poolId, address nft, uint256 tokenId) internal virtual {
    ...
    // compute fine value
    if (vars.remainAmount >= sd.unstakeFine) {
        vars.remainAmount = vars.remainAmount - sd.unstakeFine;
    } else {
        vars.extraAmount = vars.extraAmount + (sd.unstakeFine - vars.remainAmount);
        if(msg.sender != botAdmin) {
            vars.remainAmount = 0;
        }
    }

    sd.remainYieldAmount = vars.remainAmount;
    ...

    // send remain funds to owner
    if (sd.remainYieldAmount > 0) {
        underlyingAsset.safeTransfer(vars.nftOwner, sd.remainYieldAmount);
        sd.remainYieldAmount = 0;
    }
```

> Fixed in [commit 75055c9](https://github.com/BendDAO/bend-v2/commit/75055c907517c4970a2cc7d27e0e6226e366781e)
