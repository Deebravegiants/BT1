# [M] Mitigation Confirmed for Mitigation of M-04: Issue mitigated

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/36
Type: code-finding

## Details
## Mitigated issue
[M-04: Lack of deadline for uniswap AMM](https://github.com/code-423n4/2023-03-asymmetry-findings/issues/932)

The issue was that the deposit for rETH via Uniswap didn't include a deadline.

## Mitigation review
Uniswap is no longer used. Instead RocketSwapRouter is used which swaps what cannot be deposited in the pool on either Uniswap or Balancer, according to provided weights. A 100% Balancer weight has been chosen, [which sets the deadline to `block.timestamp`](https://etherscan.io/address/0x16d5a408e807db8ef7c578279beeee6b228f1c1c#code#F19#L262). (RocketSwapRouter sets the same deadline for Uniswap.)
