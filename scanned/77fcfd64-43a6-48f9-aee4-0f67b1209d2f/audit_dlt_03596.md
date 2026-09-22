# [M] M-08 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-05-gondi-mitigation
Published: 2024-05-24
Source: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/73
Type: code-finding

## Details
# Lines of code

https://github.com/pixeldaogg/florida-contracts/blob/10d48b51313496c41c886cd46e610b627ef159aa/src/interfaces/loans/IMultiSourceLoan.sol#L52


# Vulnerability details

## Issue

The borrower signature could be reused in the Loan contract. 

## Mitigation
The sponsor acknowledged and added a comment in the code. So I believed the issue is not fixed. It should be marked as Acknowledged and Out of Scope instead.
```diff
+ /// @dev It's advised that borrowers only set an expirationTime close to the actual time they will execute the loan
+ ///      to avoid replays. 
/// @param offerExecution List of offers to be filled and amount for each.
/// @param tokenId NFT collateral token ID.
```



## Assessed type

Other
