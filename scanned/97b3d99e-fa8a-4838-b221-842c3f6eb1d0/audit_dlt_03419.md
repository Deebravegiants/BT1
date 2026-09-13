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

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L304-L316
```solidity
    function withdraw(uint256 share, address receiver) public nonReentrant whenNotPaused {
        ...
    }
```

Moreover, calling the `deposit(uint256 assets, address receiver)`, `mint(uint256 shares, address receiver)`, `withdraw(uint256 assets, address receiver, address owner)`, and `redeem(uint256 shares, address receiver, address shareOwner)` functions below always revert so no `assets` can be deposited, no `shares` can be minted, no `assets` can be withdrawn, and no `share` can be redeemed through these functions; in this case, the positive values returned by the `maxDeposit`, `maxMint`, `maxWithdraw`, and `maxRedeem` functions are also incorrect and misleading.

As specified in https://eips.ethereum.org/EIPS/eip-4626:
- `maxDeposit` `MUST factor in both global and user-specific limits, like if deposits are entirely disabled (even temporarily) it MUST return 0`;
- `maxMint` `MUST factor in both global and user-specific limits, like if mints are entirely disabled (even temporarily) it MUST return 0`;
- `maxWithdraw` `MUST factor in both global and user-specific limits, like if withdrawals are entirely disabled (even temporarily) it MUST return 0`;
- `maxRedeem` `MUST factor in both global and user-specific limits, like if redemption is entirely disabled (even temporarily) it MUST return 0`.

Since the current `maxDeposit`, `maxMint`, `maxWithdraw`, and `maxRedeem` functions do not return 0 when they should, these functions are not compliant with the EIP-4626 standard even though the `AccountingManager` contract should be compliant with the EIP-4626 standard according to https://code4rena.com/audits/2024-04-noya.

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L693-L707
```solidity
    function mint(uint256 shares, address receiver) public override returns (uint256) {
        revert NoyaAccounting_NOT_ALLOWED();
    }

    function withdraw(uint256 assets, address receiver, address owner) public override returns (uint256) {
        revert NoyaAccounting_NOT_ALLOWED();
    }

    function redeem(uint256 shares, address receiver, address shareOwner) public override returns (uint256) {
        revert NoyaAccounting_NOT_ALLOWED();
    }

    function deposit(uint256 assets, address receiver) public override returns (uint256) {
        revert NoyaAccounting_NOT_ALLOWED();
    }
```

## Proof of Concept
Please add the following test in `testFoundry\TestAccounting.sol`. This test will pass to demonstrate the described scenario for the `maxDeposit` function. The cases for the `maxMint`, `maxWithdraw`, and `maxRedeem` functions are similar to it.

```solidity
    function test_maxDepositCanBeIncorrect() public {
        uint256 _amount = 10_000 * 1e6;

        _dealWhale(baseToken, address(alice), address(0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23), 10 * _amount);
        _dealWhale(baseToken, address(bob), address(0x1AB4973a48dc892Cd9971ECE8e01DcC7688f8F23), 10 * _amount);

        vm.prank(alice);
        SafeERC20.forceApprove(IERC20(USDC), address(accountingManager), _amount);

        vm.prank(bob);
        SafeERC20.forceApprove(IERC20(USDC), address(accountingManager), _amount);

        vm.prank(alice);
        accountingManager.deposit(address(alice), _amount, address(0));

        vm.startPrank(bob);

        // maxDeposit function returns type(uint256).max
        assertEq(accountingManager.maxDeposit(address(bob)), type(uint256).max);

        // yet, calling deposit(uint256 assets, address receiver) function always reverts
        vm.expectRevert();
        accountingManager.deposit(1, address(bob));

        vm.startPrank(owner);

        // many functions of AccountingManager contract are paused because of an emergency
        accountingManager.emergencyStop();

        vm.startPrank(bob);

        // maxDeposit function still returns type(uint256).max
        assertEq(accountingManager.maxDeposit(address(bob)), type(uint256).max);

        // however, calling deposit(address receiver, uint256 amount, address referrer) function reverts because it is paused
        vm.expectRevert();
        accountingManager.deposit(address(bob), 1, address(0));

        vm.stopPrank();
    }
```

## Tools Used
Manual Review

## Recommended Mitigation Steps
The `AccountingManager` contract can be updated to add the `maxDeposit`, `maxMint`, `maxWithdraw`, and `maxRedeem` functions to override the corresponding functions in OpenZeppelin's `ERC4626` contract. To be compliant with the EIP-4626 standard, these functions can always return 0 since calling the `deposit(uint256 assets, address receiver)`, `mint(uint256 shares, address receiver)`, `withdraw(uint256 assets, address receiver, address owner)`, and `redeem(uint256 shares, address receiver, address shareOwner)` functions always revert. Moreover, two more functions that are similar to the `maxDeposit` and `maxRedeem` functions can be added in the `AccountingManager` contract to accompany the `deposit(address receiver, uint256 amount, address referrer)` and `withdraw(uint256 share, address receiver)` functions, and these two additional functions should respectively return 0 when the corresponding `deposit` and `withdraw` functions are respectively paused.


## Assessed type

ERC4626
