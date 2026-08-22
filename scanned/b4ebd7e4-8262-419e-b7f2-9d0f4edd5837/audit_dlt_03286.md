# [H] Unsafe cast in IndexPool mint leads to attack

## Summary
Severity: High
Chain: Smart contract
Component: 2021-09-sushitrident
Published: 2021-09-29
Source: https://github.com/code-423n4/2021-09-sushitrident-findings/issues/77
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

The `IndexPool.mint` function performs an unsafe cast of `ratio` to the `uint120` type:

```solidity
uint120 ratio = uint120(_div(toMint, totalSupply));
```

Note that `toMint` is chosen by the caller and when choosing `toMint = 2**120 * totalSupply / BASE`, the `ratio` variable will be `2**120` and then truncated to 0 due to the cast.

This allows an attacker to mint LP tokens for free.
They just need to choose the `ratio` such that the `amountIn = ratio * reserve / BASE` variable passes the `require(amountIn >= MIN_BALANCE, "MIN_BALANCE");` check.
For example, when choosing `ratio = 2**120 * totalSupply / BASE + 1e16`, an attacker has to pay 1/100th of the current reserves but heavily inflates the LP token supply.

They can then use the inflated LP tokens they received in `burn` to withdraw the entire pool reserves.

## POC
I created this POC that implements a hardhat test and shows how to steal the pool tokens:

https://gist.github.com/MrToph/0c8b6b5ffac0673b2f72412cf4b0b099

## Impact
An attacker can inflate the LP token pool supply and mint themselves a lot of LP tokens by providing almost no tokens themselves.
The entire pool tokens can be stolen.

## Recommended Mitigation Steps
Even though Solidity 0.8.x is used, type casts do not throw an error.
A [`SafeCast` library](https://docs.openzeppelin.com/contracts/4.x/api/utils#SafeCast) must be used everywhere a typecast is done.
