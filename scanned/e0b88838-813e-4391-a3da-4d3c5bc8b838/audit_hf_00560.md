# [M] M-01 | Incorrect Bump Calculation

## Summary
Severity: Medium
Contest weight: 0.1481
Dataset id: 2022
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The criteria for a bump is described as:
That the total reserves in the system (inclusive of debt), when placed across the anchor position
(with no reserves the floor), is enough to buy back the entire circulating supply.
However, in the _canBump function the capacity is calculated with the activeX96 as the upper to the
Anchor range.
This is however flawed because the activeX96 may not reside within the new Anchor range. Instead
the anchorTick may be selected such that the activeX96 is actually within the Discovery range.
This would not be an issue if the Discovery and Anchor ranges were guaranteed to have the same
concentration of reserves.
However it is possible that the Discovery range liquidity is actually lower than the Anchor range
liquidity, in which case assuming that the reserves were evenly spread out across this range would
underestimate the capacity of the protocol and errantly indicate that a bump would not be possible
when in fact it can be.

## Recommendation
Consider executing the bump logic after the new anchorTick and liquidities of the Anchor and
Discovery ranges have been defined. Then do not allow the bump logic to change the liquidity of the
Anchor or discovery.
