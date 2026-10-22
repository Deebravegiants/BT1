# [M] Improper Handling of SupplyList in seizeInternal()

## Summary
Severity: Medium
Contest weight: 0.4097
Dataset id: 13196
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function seizeInternal(address seizerToken, address liquidator, address borrower, uint seizeTokens) internal returns (uint) {
    (vars.mathErr, vars.borrowerTokensNew) = subUInt(accountTokens[borrower], seizeTokens);
    /* We write the previously calculated values into storage */
    totalReserves = vars.totalReservesNew;
    totalSupply = vars.totalSupplyNew;
    accountTokens[borrower] = vars.borrowerTokensNew;
    accountTokens[liquidator] = vars.liquidatorTokensNew;
    return uint(Error.NO_ERROR);
```
Specifically, we show above the related implementation of the seizeInternal() routine. This routine calculates the new borrower and liquidator token balances after liquidation and writes the updated values into storage. However, our analysis shows that it only updates the balance of TToken and leaves borrower and supplier lists unchanged. In fact, without properly handling the modification of borrower and supplier lists, the information provided by BorrowList[] and SupplyList[] could be misleading.

## Recommendation
Properly handle the borrower and supplier list modification in the TToken::seizeInternal() routine.
