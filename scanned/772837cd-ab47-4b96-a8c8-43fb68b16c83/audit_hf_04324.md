# [C] C-01 | DoS By Adding Liquidity On Behalf Of BPOOL

## Summary
Severity: Critical
Contest weight: 0.5934
Dataset id: 21480
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol has three main functions, which are bump, sweep and slide, to maintain liquidity structure among different ranges. During bump, all liquidity is removed from floor, anchor and discovery, and the exactly previous amount of liquidity is added back to anchor and discovery.
```solidity
(,, uint128 liquidityA) = BPOOL.removeAllFrom(Range.ANCHOR);
(,, uint128 liquidityD) = BPOOL.removeAllFrom(Range.DISCOVERY);
// ...
BPOOL.manageLiquidityFor(Range.ANCHOR, Action.ADD, liquidityA);
BPOOL.manageLiquidityFor(Range.DISCOVERY, Action.ADD, liquidityD);
```
Normally, the protocol should never have more liquidity in anchor than discovery. However, anyone can directly mint on behalf of any other user in Uniswap. An attacker can break this invariant by adding liquidity to anchor and bumping right after. After this, the sweep will always revert due to underflow [here](https://github.com/GuardianAudits/baseline-team-2-pocs/blob/7aa793fec8884f284f09c2995b8da3bbe97a9a0a/src/policies/MarketMaking.sol#L196). slide and bump will also always revert regardless of the active price if the attack is done when the checkpointTick is equal to floorUpper + tickSpacing, and the protocol’s liquidity structure will be completely stuck.

## Recommendation
There is no way to prevent attackers minting directly on Uniswap. To prevent this issue, keep track of the protocol owned liquidity as a separate variable and use it to determine liquidity amounts.
