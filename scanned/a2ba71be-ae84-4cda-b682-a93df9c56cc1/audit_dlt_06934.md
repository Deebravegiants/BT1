# [M] `YAxisVotePower.balanceOf` can be manipulated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-09-yaxis
Published: 2021-09-15
Source: https://github.com/code-423n4/2021-09-yaxis-findings/issues/113
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

The `YAxisVotePower.balanceOf` contract uses the Uniswap pool reserves to compute a `_lpStakingYax` reward:

```solidity
(uint256 _yaxReserves,,) = yaxisEthUniswapV2Pair.getReserves();
int256 _lpStakingYax = _yaxReserves
      .mul(_stakeAmount)
      .div(_supply)
      .add(rewardsYaxisEth.earned(_voter));
```

The pool can be temporarily manipulated to increase the `_yaxReserves` amount.

## Impact
If this voting power is used for governance proposals, an attacker can increase their voting power and pass a proposal.

## Recommended Mitigation Steps
One could build a TWAP-style contract that tracks a time-weighted-average reserve amount (instead of the price in traditional TWAPs).
This can then not be manipulated by flashloans.
