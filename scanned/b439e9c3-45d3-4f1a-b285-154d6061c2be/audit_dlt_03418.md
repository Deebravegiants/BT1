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


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-04-noya-findings/issues/1522_
