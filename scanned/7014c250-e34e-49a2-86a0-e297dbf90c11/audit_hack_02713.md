# [H] VaultInternal.sol : The function "_withdraw" is not following the standard ERC4626 vault standard while withdrawing the shares

## Summary
Severity: High
Reporter: ak1
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L174-L189
Type: audit-issue

## Details
# VaultInternal.sol : The function "_withdraw" is not following the standard ERC4626 vault standard while withdrawing the shares

## Summary
VaultInternal.sol : The function "_withdraw" is not following the standard ERC4626 vault standard while withdrawing the share.
The function `_previewWithdraw`  is returning the rounded down values. Due to this, the user could receive the lesser shares.

## Vulnerability Detail
The function `_withdraw` is using the  `_previewWithdraw` from `ERC4626BaseInternal.sol`
When we look at the calculation part, the calculated share value is rounded down. 
    function _previewMint(uint256 shareAmount)
        internal
        view
        virtual
        returns (uint256 assetAmount)
    {
        uint256 supply = _totalSupply();

        if (supply == 0) {
            assetAmount = shareAmount;
        } else {
            assetAmount = (shareAmount * _totalAssets() + supply - 1) / supply;
        }
    }

Lets say when shareAmount = 2, then the user should be allowed to get 2 units of assets.

But, in blow situation, user could receive the lesser then what is expected.
For calculation lets consider,
shareAmount = 2
_totalAssets = 5
supply = 10

as per calculation the numerator will be `(shareAmount * _totalAssets() + supply - 1)` = `19`
when we divide the 19 by 10, we will get 1 (due to solidity's division will round down)

## Impact

User might receive lesser share amount than what is allocated.

Refer the below link for detailed analysis about this kind of issue which is related to ERC4626 implementation.
https://github.com/code-423n4/2022-06-notional-coop-findings/issues/155

## Code Snippet
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/vault/VaultInternal.sol#L174-L189
## Tool used

Manual Review

## Recommendation
Follow the rounding up rule for withdraw.
Refer the recommendations suggested from the link https://github.com/code-423n4/2022-06-notional-coop-findings/issues/155
