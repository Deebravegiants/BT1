# [H] No error handling leads to loss of lender funds

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/156
Type: sherlock-finding

## Details
Tomo

high

# No error handling leads to loss of lender funds

## Summary

No error handling leads to loss of lender funds

## Vulnerability Detail

If the external call in `convert()` failed, there is no error handling, users can’t notice it. 

### Example

1. redeemer calls the `[redeem](https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Redeemer.sol#L214-L333)`
2. Lender sends 1000 principal token from Lender to Redeemer contract
[https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Redeemer.sol#L267-L272](https://github.com/sherlock-audit/2022-10-illuminate/blob/main/src/Redeemer.sol#L267-L272)

```solidity
// Receive the principal token from the lender contract
  Safe.transferFrom(
      IERC20(principal),
      cachedLender,
      address(this),
      amount
  );
```

1. And try to convert from compounding assets to the underlying asset by `IConverter(converter).convert`

2. The external call failed in the `convert()` but, this transaction success due to insufficient error handling

```solidity
try IAaveAToken(c).POOL() returns (address pool) {
    // Allow the pool to spend the funds
	    Safe.approve(IERC20(u), pool, a);
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/156_
