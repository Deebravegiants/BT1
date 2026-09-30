# [M] Borrower can obtain principle

## Summary
Severity: Medium
Contest weight: 0.6906
Dataset id: 1848
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Internal pre-conditions  
External pre-conditions  
Attack Path  

Assume that the ratio/price is 1e18 (1 XYZ per ABC => Principle per Collateral). XYZ is 18 decimals while ABC is 6 decimals.  
Assume that Bob (malicious borrower) calls the permissionless DebitaV3Aggregator.matchOffersV3 function. The amount of collateral deducted from Bob's borrow offer is calculated via the following:  
userUsedCollateral = (lendAmountPerOrder[i] * (10 ** decimalsCollateral)) / ratio;  
userUsedCollateral = (lendAmountPerOrder[i] * 1e6) / 1e18;  
ontracts/contracts/DebitaV3Aggregator.sol#L467  

File: DebitaV3Aggregator.sol
```solidity
function matchOffersV3(
    ..SNIP..
    // calculate the amount of collateral used by the lender
    uint userUsedCollateral = (lendAmountPerOrder[i] * (10 ** decimalsCollateral)) / ratio;
```

For lendAmountPerOrder, he uses a value that is small enough to trigger a rounding to zero error. The range of lendAmountPerOrder that will cause userUsedCollateral to round down to zero is:  
0 ≤ lendAmountPerOrder < 1012  

Thus, for each offer, Bob will specify the lendAmountPerOrder[i] to be 1e12 - 1. Thus, for each offer, he will be able to obtain 1e12 - 1 XYZ tokens without paying a single ABC tokens as collateral.  

This attack is profitable because each matchOffersV3 transaction can execute up to 100 offers, and the protocol is intended to be deployed on L2 chains where gas fees are extremely cheap or even negligible.  
ontracts/contracts/DebitaV3Aggregator.sol#L290  

File: DebitaV3Aggregator.sol
```solidity
function matchOffersV3(
    ..SNIP..
    // check lendOrder length is less than 100
    require(lendOrders.length <= 100, "Too many lend orders");
```

Following is the extract from Contest’s README showing that the protocol will be deployed to following L2 chains.  
Q: On what chains are the smart contracts going to be deployed?  
Sonic (Prev. Fantom), Base, Arbitrum & OP  
High. Loss of assets.

## Recommendation
above attack.
```solidity
// calculate the amount of collateral used by the lender
uint userUsedCollateral = (lendAmountPerOrder[i] * (10 ** decimalsCollateral)) / ratio;
//+
require(userUsedCollateral > 0, "userUsedCollateral is zero");
```
