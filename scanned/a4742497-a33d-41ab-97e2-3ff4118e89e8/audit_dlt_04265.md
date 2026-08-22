# [M] Redeemed amount in Redeemer.sol#authRedeem may be truncated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-illuminate
Published: 2022-11-10
Source: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/148
Type: sherlock-finding

## Details
ctf_sec

medium

# Redeemed amount in Redeemer.sol#authRedeem may be truncated

## Summary

Redeemed amount in Redeemer.sol#authRedeem may be truncated

## Vulnerability Detail

Let us look into the implementation for Redeemer.sol#authRedeem

```solidity
  // Get the principal token for the given market
  IERC5095 pt = IERC5095(IMarketPlace(marketPlace).token(u, m, 0));

  // Make sure the market has matured
  uint256 maturity = pt.maturity();
  if (block.timestamp < maturity) {
      revert Exception(7, maturity, 0, address(0), address(0));
  }

  // Calculate the amount redeemed
  uint256 redeemed = (a * holdings[u][m]) / pt.totalSupply();

  // Update holdings of underlying
  holdings[u][m] = holdings[u][m] - redeemed;
  
  // Burn the user's principal tokens
  pt.authBurn(f, a);
  
  // Transfer the original underlying token back to the user
  Safe.transfer(IERC20(u), t, redeemed);
```

note the line:

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-illuminate-judging/issues/148_
