# [M] AccountingManager has no correct implementations of the core ERC-4626 functions `deposit`, `mint`, `withdraw` and `redeem`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1334
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L200
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L304
https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L693-L707


# Vulnerability details




## Impact
There are no ERC-4626 compliant implementations of the `deposit`, `mint`, `withdraw` and `redeem` functions.

## Proof of Concept
[AccountingManager is to be ERC-4626 compliant](https://github.com/code-423n4/2024-04-noya?tab=readme-ov-file#:~:text=src/accountingManager/AccountingManager,ERC4626). Therefore it is expected to have `deposit`, `mint`, `withdraw` and `redeem` functions implemented according to the specifications.

However, [`deposit`, `mint`, `withdraw` and `redeem` all simply revert](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L693-L707).
There is an [alternative version of `deposit()`](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L200-L219) which takes an additional `address referrer` input and does not emit the `Deposit` event.
There is an [alternative version of `withdraw()`](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/accountingManager/AccountingManager.sol#L304-L316) which omits the `address owner` input and does not emit the `Withdraw` event. This `withdraw()` does not withdraw assets but burns shares, i.e. it should rather have been called `redeem()`.
Thus none of the core functions of ERC-4626 are correctly implemented, which makes it all but impossible to integrate with AccountingManager as an ERC-4626 vault.

## Recommended Mitigation Steps
Consider implementing `deposit()`, `mint()`, `withdraw()` and `redeem()` according to ERC-4626.


## Assessed type

ERC4626
