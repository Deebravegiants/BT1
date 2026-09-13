# [M] M-12 Unmitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-revert-mitigation
Published: 2024-04-29
Source: https://github.com/code-423n4/2024-04-revert-mitigation-findings/issues/89
Type: code-finding

## Details
# Lines of code

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol?plain=1#L961-L963


# Vulnerability details

## C4 issue

M-12: Wrong global lending limit check in _deposit function


## Comments

Revert utilizes a global lend limit to ensure that lenders do not exceed a global lend limit. Unfortunately, the global lend limit is denominated in assets. The value it compares itself to is `totalSupply()`, which is denominated in shares. This comparison is invalid since both values are in different denominations.
 
 
## Lines of code

https://github.com/revert-finance/lend/blob/audit/src/V3Vault.sol?plain=1#L961-L963

## Vulnerability details

The _deposit() function incorrectly utilizes the wrong denomination when comparing the globalLendLimit to the number of shares. The globalLendLimit denomination is set in assets. However, `totalSupply() + shares` denomination is set in shares. This makes this comparison check incorrect and can lead to more assets being lent than anticipated. 
 
## Impact

More assets may be deposited than expected. 

 
## Proof of Concept

Reviewing the function below:

```solidity
if (totalSupply() + shares > globalLendLimit) {
    revert GlobalLendLimit();
}
```

Since `totalSupply() + shares` are denominated as shares and globalLendLimit as assets, the comparison is incorrect.

 
## Tools Used

Manual review

## Recommended Mitigation Steps

Convert the `totalSupply() + shares` to the correct denomination in assets:

```solidity
uint256 totalSharesDenominatedInAssets = _convertToAssets(totalSupply() + shares, newLendExchangeRateX96, Math.Rounding.Up);
if (totalSharesDenominatedInAssets > globalLendLimit) {
      revert GlobalLendLimit();
}
```
 
## Assessed type

Math 


## Assessed type

Math
