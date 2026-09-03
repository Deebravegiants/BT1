# [M] Fee-on-Transfer tokens cause problems in multiple places 

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-07-benddao
Published: 2024-08-16
Source: https://github.com/code-423n4/2024-07-benddao-findings/issues/32
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-07-benddao/blob/main/src/libraries/logic/VaultLogic.sol#L428-L438


# Vulnerability details


## Description

The protocol is designed to ensure it is compatible with fee-on-transfer tokens (Fee-on-transfer is in scope). For example, the `erc20TransferInLiquidity()` function checks the balance before and after, and calculates the difference between these values to measure the tokens received

```solidity
File: VaultLogic.sol

448:   function erc20TransferInBidAmount(DataTypes.AssetData storage assetData, address from, uint256 amount) internal {
449:     address asset = assetData.underlyingAsset;
450:     uint256 poolSizeBefore = IERC20Upgradeable(asset).balanceOf(address(this));
451: 
452:     assetData.totalBidAmout += amount;
453: 
454:     IERC20Upgradeable(asset).safeTransferFrom(from, address(this), amount);
455: 
456:     uint256 poolSizeAfter = IERC20Upgradeable(asset).balanceOf(address(this));
457:     require(poolSizeAfter == (poolSizeBefore + amount), Errors.INVALID_TRANSFER_AMOUNT);
458:   }
```
But at the end of the logic, it has a required check if the contract received the exact intended amount 
 these two features are not compatible If the `asset` is Fee-on-transfer tokens the requirement will keep revert

Example:
1- Contract balanceOf is 2000 of Fee-on-transfer tokens
2- Contract transfer from user `amount == 1000` 
3- Fee is collected, so the contract received only 950 tokens, But the require will check ** 2000 + 1000 ==  2950 ** and revert

## Impact

Any function/feature that calls 

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-07-benddao-findings/issues/32_
