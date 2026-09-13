# [M] `AccountingManager` contract's `previewDeposit`, `previewMint`, `previewWithdraw`, and `previewRedeem` functions are not compliant with EIP-4626 standard

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1522
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/cc3854f634a72bd4a8b597021887088ca2d6d29f/contracts/accountingManager/AccountingManager.sol#L693-L707
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol#L151-L168


# Vulnerability details

## Impact
The `AccountingManager` contract's `deposit(uint256 assets, address receiver)`, `mint(uint256 shares, address receiver)`, `withdraw(uint256 assets, address receiver, address owner)`, and `redeem(uint256 shares, address receiver, address shareOwner)` functions below always revert.

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

According to https://eips.ethereum.org/EIPS/eip-4626:
- `previewDeposit` `MUST return as close to and no more than the exact amount of Vault shares that would be minted in a ``deposit`` call in the same transaction` and `MAY revert due to other conditions that would also cause ``deposit`` to revert`;
- `previewMint` `MUST return as close to and no fewer than the exact amount of assets that would be deposited in a ``mint`` call in the same transaction` and `MAY revert due to other conditions that would also cause ``mint`` to revert`;
- `previewWithdraw` `MUST return as close to and no fewer than the exact amount of Vault shares that would be burned in a ``withdraw`` call in the same transaction` and `MAY revert due to other conditions that would also cause ``withdraw`` to revert`;
- `previewRedeem` `MUST return as close to and no more than the exact amount of assets that would be withdrawn in a ``redeem`` call in the same transaction` and `MAY revert due to other conditions that would also cause ``redeem`` to revert`.

Yet, although no `assets` can be deposited, no `shares` can be minted, no `assets` can be withdrawn, and no `share` can be redeemed through such `deposit`, `mint`, `withdraw`, and `redeem` functions, the `AccountingManager` contract's `previewDeposit`, `previewMint`, `previewWithdraw`, and `previewRedeem` functions below can still return positive values, which are incorrect based on the EIP-4626 standard. Hence, these `previewDeposit`, `previewMint`, `previewWithdraw`, and `previewRedeem` functions are not compliant with the EIP-4626 standard though https://code4rena.com/audits/2024-04-noya states that the `AccountingManager` contract should be compliant with the EIP-4626 standard.

https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/extensions/ERC4626.sol#L151-L168
```solidity
    function previewDeposit(uint256 assets) public view virtual returns (uint256) {
        return _convertToShares(assets, Math.Rounding.Floor);
    }
    ...
    function previewMint(uint256 shares) public view virtual returns (uint256) {
        return _convertToAssets(shares, Math.Rounding.Ceil);
    }
    ...
    function previewWithdraw(uint256 assets) public view virtual returns (uint256) {
        return _convertToShares(assets, Math.Rounding.Ceil);
    }
    ...
    function previewRedeem(uint256 shares) public view virtual returns (uint256) {
        return _convertToAssets(shares, Math.Rounding.Floor);
    }
```

## Proof of Concept
Please add the following test in `testFoundry\TestAccounting.sol`. This test will pass to demonstrate the described scenario for the `previewMint` function. The cases for the `previewDeposit`, `previewWithdraw`, and `previewRedeem` functions are similar to it.

```solidity
    function test_previewMintCanBeIncorrect() public {
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

        // this previewMint function call shows that
        //   no fewer than _amount of assets would be deposited in a mint function call for minting _amount shares in the same transaction
        assertEq(accountingManager.previewMint(_amount), _amount);

        // however, calling mint function always revert so no shares can be minted and no assets can be deposited through such mint function,
        //   which means that previewMint function is incorrect
        vm.expectRevert();
        accountingManager.mint(_amount, address(bob));

        vm.stopPrank();
    }
```

## Tools Used
Manual Review

## Recommended Mitigation Steps
The `previewDeposit`, `previewMint`, `previewWithdraw`, and `previewRedeem` functions in the `AccountingManager` contract can be updated to revert because the corresponding `deposit`, `mint`, `withdraw`, and `redeem` functions all revert. Then, the `AccountingManager` contract can further add a function, which is similar to OpenZeppelin's `previewDeposit` function, to replace the `previewDeposit` function's usage in the `calculateDepositShares` and `recordProfitForFee` functions and add a function, which is similar to OpenZeppelin's `previewRedeem` function, to replace the `previewRedeem` function's usage in the `calculateWithdrawShares` function.


## Assessed type

Other
