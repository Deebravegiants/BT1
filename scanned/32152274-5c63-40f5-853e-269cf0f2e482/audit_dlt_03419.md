# [M] `maxDeposit`, `maxMint`, `maxWithdraw`, and `maxRedeem` functions do not return 0 when they should

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1517
Type: code-finding

## Details
# Lines of code

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol#L131-L148
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L200-L219
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L304-L316
https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L693-L707


# Vulnerability details

## Impact
The `AccountingManager` contracts' `maxDeposit` and `maxMint` functions below always return `type(uint256).max` and `maxWithdraw` and `maxRedeem` functions below would return positive values when `balanceOf(owner)` is positive. However, when the `deposit(address receiver, uint256 amount, address referrer)` and `withdraw(uint256 share, address receiver)` functions below are paused, calling these functions would revert in which no `amount` can be deposited and no `share` can be withdrawn; in this case, the positive values returned by the `maxDeposit`, `maxMint`, `maxWithdraw`, and `maxRedeem` functions are incorrect and misleading.

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol#L131-L148
```solidity
    function maxDeposit(address) public view virtual returns (uint256) {
        return type(uint256).max;
    }
    ...
    function maxMint(address) public view virtual returns (uint256) {
        return type(uint256).max;
    }
    ...
    function maxWithdraw(address owner) public view virtual returns (uint256) {
        return _convertToAssets(balanceOf(owner), Math.Rounding.Floor);
    }
    ...
    function maxRedeem(address owner) public view virtual returns (uint256) {
        return balanceOf(owner);
    }
```

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L200-L219
```solidity
    function deposit(address receiver, uint256 amount, address referrer) public nonReentrant whenNotPaused {
        ...
    }
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1517_
