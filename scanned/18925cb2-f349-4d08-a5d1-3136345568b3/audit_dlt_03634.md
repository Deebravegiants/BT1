# [M] getActiveTickIndex implementation error

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-09-goodentry-mitigation
Published: 2023-09-11
Source: https://github.com/code-423n4/2023-09-goodentry-mitigation-findings/issues/43
Type: code-finding

## Details
# Lines of code

https://github.com/GoodEntry-io/ge/blob/c7c7de57902e11e66c8186d93c5bb511b53a45b8/contracts/GeVault.sol#L470


# Vulnerability details

## Impact

The implementation of getActiveTickIndex is wrong, and the searched ticks do not meet expectations, causing funds to be incorrectly allocated to edge ticks, and there is basically no staking income.

## Proof of Concept

```solidity
    // if base token is token0, ticks above only contain base token = token0 and ticks below only hold quote token = token1
    if (newTickIndex > 1) 
      depositAndStash(
        ticks[newTickIndex-2], 
        baseTokenIsToken0 ? 0 : availToken0 / liquidityPerTick,
        baseTokenIsToken0 ? availToken1 / liquidityPerTick : 0
      );


  /// @notice Return first valid tick
  function getActiveTickIndex() public view returns (uint activeTickIndex) {
    // loop on all ticks, if underlying is only base token then we are above, and tickIndex is 2 below
    for (uint tickIndex = 0; tickIndex < ticks.length; tickIndex++){
      (uint amt0, uint amt1) = ticks[tickIndex].getTokenAmountsExcludingFees(1e18);
      // found a tick that's above price (ie its only underlying is the base token)
      if( (baseTokenIsToken0 && amt0 == 0) || (!baseTokenIsToken0 && amt0 == 0) ) return tickIndex;
    }
    // all ticks are below price
    return ticks.length;
  }
```

According to code comments:
- If baseTokenIsToken0 is true, ticks above current price only contain base token, that is token0, so amt1 is 0.

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-09-goodentry-mitigation-findings/issues/43_
