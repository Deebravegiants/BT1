# [M] principal value for element, pendle, APWine, Tempus, and Sense lending function is not validated.

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/140
Type: sherlock-finding

## Details
ctf_sec

medium

# principal value for element, pendle, APWine, Tempus, and Sense lending function is not validated.

## Summary

principal value for element, pendle, APWine, Tempus, and Sense lending function is not validated.

## Vulnerability Detail

Note in the lending function for illuminate and yield protocol validates the principal value.

```solidity
// Check that the principal is Illuminate or Yield
  if (
      p != uint8(MarketPlace.Principals.Illuminate) &&
      p != uint8(MarketPlace.Principals.Yield)
  ) {
      revert Exception(6, 0, 0, address(0), address(0));
  }
``` 

same validation is implemented in Swivel.

```solidity
// Check that the principal is Swivel
    if (p != uint8(MarketPlace.Principals.Swivel)) {
        revert Exception(
            6,
            p,
            uint8(MarketPlace.Principals.Swivel),
            address(0),
            address(0)
        );
 }
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/140_
