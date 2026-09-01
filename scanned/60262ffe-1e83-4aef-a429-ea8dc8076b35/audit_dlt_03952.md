# [H] Incorrect Spot Price

## Summary
Severity: High
Chain: Smart contract
Component: 2023-10-notional
Published: 2023-11-25
Source: https://github.com/sherlock-audit/2023-10-notional-judging/issues/81
Type: sherlock-finding

## Details
xiaoming90

high

# Incorrect Spot Price

## Summary

Multiple discrepancies between the implementation of Leverage Vault's `_calcSpotPrice` function and SDK were observed, which indicate that the computed spot price is incorrect.

If the spot price is incorrect, it might potentially fail to detect the pool has been manipulated. In the worst-case scenario, the trade proceeds to execute against the manipulated pool, leading to a loss of assets.

## Vulnerability Detail

The `BalancerSpotPrice._calculateStableMathSpotPrice` function relies on the `StableMath._calcSpotPrice` to compute the spot price of two tokens.

https://github.com/sherlock-audit/2023-10-notional/blob/main/leveraged-vaults/contracts/vaults/balancer/BalancerSpotPrice.sol#L93

```solidity
File: BalancerSpotPrice.sol
78:     function _calculateStableMathSpotPrice(
..SNIP..
86:         // Apply scale factors
87:         uint256 secondary = balances[index2] * scalingFactors[index2] / BALANCER_PRECISION;
88: 
89:         uint256 invariant = StableMath._calculateInvariant(
90:             ampParam, StableMath._balances(scaledPrimary, secondary), true // round up
91:         );
92: 
93:         spotPrice = StableMath._calcSpotPrice(ampParam, invariant, scaledPrimary, secondary);
```

https://github.com/sherlock-audit/2023-10-notional/blob/main/leveraged-vaults/contracts/vaults/balancer/math/StableMath.sol#L90

```solidity
File: StableMath.sol
087:     /**
088:      * @dev Calculates the spot price of token Y in token X.
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2023-10-notional-judging/issues/81_
