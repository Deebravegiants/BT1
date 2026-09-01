# [H] Tempus depositAndFix function signature mismatch in Lender.sol

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/141
Type: sherlock-finding

## Details
ctf_sec

high

# Tempus depositAndFix function signature mismatch in Lender.sol

## Summary

Tempus depositAndFix function signature mismatch in Lender.sol

## Vulnerability Detail

The lending function for tempus is implemented below

```solidity
// Get the Tempus Router from the principal token
address controller = ITempusPool(ITempusToken(principal).pool())
    .controller();

// Swap on the Tempus Router using the provided market and params
ITempus(controller).depositAndFix(x, lent, true, r, d);
```

note x is /// @param x Tempus AMM that executes the swap

We can look into the ITempus interface 

```solidity
interface ITempus {
    function depositAndFix(
        address,
        uint256,
        bool,
        uint256,
        uint256
    ) external;
```


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/141_
