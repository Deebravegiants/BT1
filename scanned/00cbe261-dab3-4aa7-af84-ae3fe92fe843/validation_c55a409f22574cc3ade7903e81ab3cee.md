After thoroughly analyzing the Metric OMM codebase against the external bug's invariant class (order-dependent, accumulator-based fee distribution where early claimers extract more than their fair share), here is my assessment:

**External bug class mapped to Metric OMM invariants:**
- Order-dependent LP claim: early removers extract more than proportional share
- Accumulator using optimistic/stale divisor rather than actual funded amount
- Asymmetric default risk / MEV advantage for early actors

**LP fee distribution (`LiquidityLib.removeLiquidity`):**

The LP fee in Metric OMM is embedded directly in bin balances. When a swap occurs, the input token (minus protocol spread fee) enters the bin. When an LP removes liquidity, they receive:

```solidity
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint