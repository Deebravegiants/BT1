Looking at the external report's bug class — an unvalidated external address used in a callback that drains tokens — I need to trace the analog in Metric OMM across the swap callback path, the liquidity callback path, and the periphery routers.

**Swap callback path (`MetricOmmPool.swap` → `metricOmmSwapCallback`):**

The pool calls back `msg.sender` after computing deltas and sending output tokens: [1](#0-0) 

The pool then enforces a balance check (`IncorrectDelta`) after the callback returns, so underpayment reverts. The pool itself does not validate who `msg.sender` is — that responsibility is delegated to the callback implementer.

**Router callback validation

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L257-263)
```text
      uint256 balance0Before = balance0();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount0Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
        revert IncorrectDelta();
      }
```
