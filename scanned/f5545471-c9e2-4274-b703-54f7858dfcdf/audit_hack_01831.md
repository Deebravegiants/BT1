# [M] Underflow if TOKEN_DECIMALS are greater than 18

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

In `latestAnswer()`, the assumption is made that `TOKEN_DECIMALS` is less than 18:


**code/contracts/proxies/CmpPriceProvider.sol:L76**
```solidity
(_ethBalanceOfCpmToken.mul(1 ether)  + _tokenBalanceOfCpmToken.mul(_unsignedTokenPrice).mul(10**(18-TOKEN_DECIMALS)))
```

If there are greater than 18 decimals, then this value will underflow to a number close to MAX_UINT. 

#### Recommendation

Add a simple check to the constructor to ensure the added token has 18 decimals or less.
