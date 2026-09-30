# [M] LCY-2 | Zero Slippage Protection On Swaps

## Summary
Severity: Medium
Contest weight: 0.1044
Dataset id: 20516
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the rebalanceGmi function, if isOppositeDirection is true, it attempts to swap one token for the other to rebalance before the minting and burning processes. This is achieved by swapping through UniswapV3.

When the swap is executed, the _minOut is set to zero. This means that regardless of how much slippage the swap incurs, the execution will continue. This poses a security risk, as attackers can perform a sandwich attack on this swap on UniswapV3 and steal funds if they have sufficient capital.

The impact of this is that any attempt to rebalance while isOppositeDirection is true will lead to an excess loss of funds due to the lack of slippage protection.

## Recommendation
Set a _minOut value so that swaps do not incur more slippage than expected.
