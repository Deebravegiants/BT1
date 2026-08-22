# [M] User can prevent liquidation by enter another market that have low supply and borrow activity

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-moonwell
Published: 2023-07-31
Source: https://github.com/code-423n4/2023-07-moonwell-findings/issues/239
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/MToken.sol#L1263-L1273
https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/MToken.sol#L358
https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/MToken.sol#L402


# Vulnerability details

## Impact
Users can prevent themselves from being liquidated by entering another market that has low supply/borrow activity or have low/volatile value compared to other markets, the detailed scenario will be explained in PoC.

## Proof of Concept

The scenario :
- Alice enter market A, supply and borrow in that market.
- Alice enter market B that have low supply and borrow or low value compared to market A.
- Alice call `_addReserves` in market B so that `totalReserves` is bigger than `totalCash` + `totalBorrows`.
- After some time Alice has shortfall (his borrow value bigger than supply value).
- Another user try to liquidate Alice and seize her market A collateral by calling `liquidateBorrow` :

https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/MErc20.sol#L139-L142

```solidity
    function liquidateBorrow(address borrower, uint repayAmount, MTokenInterface mTokenCollateral) override external returns (uint) {
        (uint err,) = liquidateBorrowInternal(borrower, repayAmount, mTokenCollateral);
        return err;
    }
```

It will eventually trigger comptroller's `liquidateBorrowAllowed` hook :

https://github.com/code-423n4/2023-07-moonwell/blob/main/src/core/MToken.sol#L970

```solidity
    function liquidateBorrowFresh(address liquidator, address borrower, uint repayAmount, MTokenInterface mTokenCollateral) internal returns (uint, uint) {
        /* Fail if liquidate not allowed */
        uint allowed = comptroller.liquidateBorrowAllowed(address(this), address(mTokenCollateral), liquidator, borrower, repayAmount);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-moonwell-findings/issues/239_
