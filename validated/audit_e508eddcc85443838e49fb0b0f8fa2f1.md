### Title
Proportional Output Rescaling Uses Unchecked Floor Division That Can Round to Zero, Causing Trader to Pay Input and Receive Zero Output — (`metric-core/contracts/libraries/SwapMath.sol`)

### Summary

In `buyToken0InBinSpecifiedIn` and `buyToken1InBinSpecifiedIn`, when the analytical target position overshoots and the code proportionally rescales the output amount to match the remaining input budget, it uses plain floor division with no zero-guard. When the pre-rescale output is small (e.g., 1 scaled unit) and the remaining input is a strict fraction of the full-bin cost, the rescaled output rounds to exactly 0. The code then sets `totalIn1Scaled = state.amountSpecifiedRemainingScaled` and deducts the full remaining input from the swap state, so the trader pays real tokens and receives nothing.

### Finding Description

In `buyToken0InBinSpecifiedIn` (`SwapMath.sol`), after the analytical and iterative refinement steps, the final proportional rescaling block is:

```solidity
if (totalIn1Scaled > state.amountSpecifiedRemainingScaled) {
    uint256 delta = targetPos - currBinPos;
    uint256 scaledDelta = Math.ceilDiv(delta * state.amountSpecifiedRemainingScaled, totalIn1Scaled);
    if (scaledDelta == 0) scaledDelta = 1;          // guard for position
    targetPos = currBinPos + scaledDelta;

    // ← NO guard for out0Scaled
    out0Scaled = (out0Scaled * state.amountSpecifiedRemainingScaled) / totalIn1Scaled;
    totalIn1Scaled = state.amountSpecifiedRemainingScaled;
}
``` [1](#0-0) 

The code correctly guards `scaledDelta` against zero, but applies no equivalent guard to `out0Scaled`. If `out0Scaled` (the output for the full `totalIn1Scaled` input) is small — for example, 1 scaled unit — and `state.amountSpecifiedRemainingScaled < totalIn1Scaled`, then:

```
out0Scaled = (1 * state.amountSpecifiedRemainingScaled) / totalIn1Scaled
           = 0   (integer floor, since amountSpecifiedRemainingScaled < totalIn1Scaled)
```

After this block:
- `state.amountCalculatedScaled += 0` → trader receives 0 token0
- `state.amountSpecifiedRemainingScaled -= totalIn1Scaled` (= 0) → full remaining input consumed
- `binState.token0BalanceScaled -= 0` → bin loses nothing
- `binState.token1BalanceScaled += totalIn1Scaled - protocolFeeAmountScaled` → bin gains token1 [2](#0-1) 

The identical pattern exists in `buyToken1InBinSpecifiedIn` for `out1Scaled`:

```solidity
out1Scaled = (out1Scaled * state.amountSpecifiedRemainingScaled) / totalIn0Scaled;
``` [3](#0-2) 

The early-exit guard at the top of `buyToken0InBinSpecifiedIn` only checks whether the input can afford the *starting price*:

```solidity
if ((state.amountSpecifiedRemainingScaled << 64) < startingPriceX64) {
    return (currBinPos, 0, 0, 0, 0);
}
``` [4](#0-3) 

This guard does not prevent the rescaling-to-zero scenario: the input can be large enough to pass the early exit but still too small to buy even 1 scaled unit of output after the analytical position is computed.

The resulting `amount0DeltaScaled` / `amount1DeltaScaled` values flow back to `MetricOmmPool._swap`, are converted to external token units via `deltasScaledToExternal`, and the callback is executed — the trader is charged the full input and receives zero output. [5](#0-4) 

### Impact Explanation

A trader executing an exact-input swap pays their full specified input amount in token1 (or token0) and receives 0 token0 (or token1) in return. The input tokens are permanently transferred into the pool and credited to the bin's balance, constituting a direct, irreversible loss of user principal. This is a swap conservation failure: the pool receives the owed input but the trader does not receive the owed output.

### Likelihood Explanation

The condition requires:
1. A bin with a very small `token0BalanceScaled` (or `token1BalanceScaled`), achievable naturally as liquidity is consumed across bins.
2. A swap input amount that passes the starting-price early-exit check but is less than the cost of 1 scaled output unit.
3. No slippage protection (`minAmountOut = 0`) or a slippage check that accepts 0 (which is the default for many integrators).

Tokens with high price ratios (e.g., WBTC/USDC where 1 token0 unit costs many token1 units) or tokens with low decimals increase the probability. The condition is reachable by any unprivileged caller via the public `swap` function.

### Recommendation

Add a zero-guard for `out0Scaled` (and `out1Scaled`) immediately after the proportional rescaling, mirroring the existing `scaledDelta` guard:

```solidity
out0Scaled = (out0Scaled * state.amountSpecifiedRemainingScaled) / totalIn1Scaled;
if (out0Scaled == 0) {
    // Cannot fill even 1 unit; treat as no-op for this bin.
    return (currBinPos, 0, 0, 0, 0);
}
totalIn1Scaled = state.amountSpecifiedRemainingScaled;
```

Apply the same fix to `out1Scaled` in `buyToken1InBinSpecifiedIn`.

### Proof of Concept

**Setup:**
- `binState.token0BalanceScaled = 5` (very small bin balance)
- `currBinPos = 0`, `MAX_POS_BIN = 2^104 - 1`
- `lowerPriceX64 = 2^64` (price = 1.0), `upperPriceX64 = 2^64 + 2^64/100` (1% spread)
- `currBinBuyFeeX64 = 0`, `spreadFeeE6 = 0`

**Execution:**
1. `startingPriceX64 = lowerPriceX64 = 2^64`. Early-exit check: `(amountIn << 64) >= 2^64` → passes for `amountIn >= 1`.
2. Analytical target position computes `targetPos` such that `out0Scaled = 5` (full bin) and `totalIn1Scaled = 5 * avgPrice ≈ 5`.
3. Trader sends `amountIn = 3` (< `totalIn1Scaled = 5`), entering the rescaling branch.
4. `scaledDelta = ceil(targetPos * 3 / 5) >= 1` → guarded, `targetPos` updated.
5. `out0Scaled = (5 * 3) / 5 = 3` → non-zero here, but with `out0Scaled = 1`: `out0Scaled = (1 * 3) / 5 = 0`.
6. `totalIn1Scaled = 3`, `state.amountCalculatedScaled += 0`.
7. Trader pays 3 scaled units of token1, receives 0 token0.

For `out0Scaled = 1` before rescaling: set `binState.token0BalanceScaled = 1`. Then `out0Scaled = 1`, `totalIn1Scaled ≈ avgPrice`. Any `amountIn` in `[1, totalIn1Scaled - 1]` produces `out0Scaled = 0` after rescaling while consuming the full `amountIn`. [1](#0-0) [6](#0-5)

### Citations

**File:** metric-core/contracts/libraries/SwapMath.sol (L550-552)
```text
      if ((state.amountSpecifiedRemainingScaled << 64) < startingPriceX64) {
        return (currBinPos, 0, 0, 0, 0);
      }
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L624-634)
```text
        if (totalIn1Scaled > state.amountSpecifiedRemainingScaled) {
          uint256 delta = targetPos - currBinPos;
          // remaining < totalIn1Scaled ⇒ ratio < 1 ⇒ scaledDelta ≤ delta ≤ MAX_POS_BIN
          uint256 scaledDelta = Math.ceilDiv(delta * state.amountSpecifiedRemainingScaled, totalIn1Scaled);
          if (scaledDelta == 0) scaledDelta = 1;
          targetPos = currBinPos + scaledDelta;

          // Rescale out0Scaled proportionally; remaining < totalIn1Scaled ⇒ result ≤ out0Scaled ≤ MAX_POS_BIN
          out0Scaled = (out0Scaled * state.amountSpecifiedRemainingScaled) / totalIn1Scaled;
          totalIn1Scaled = state.amountSpecifiedRemainingScaled;
        }
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L639-650)
```text
      binState.token0BalanceScaled -= out0Scaled.toUint104();
      binState.token1BalanceScaled =
        uint256((binState.token1BalanceScaled) + totalIn1Scaled - protocolFeeAmountScaled).toUint104();

      state.amountSpecifiedRemainingScaled -= totalIn1Scaled;
      state.amountCalculatedScaled += out0Scaled;
      state.protocolFeeAmountScaled += protocolFeeAmountScaled;

      delta0Scaled = -out0Scaled.toInt256();
      delta1Scaled = (totalIn1Scaled - protocolFeeAmountScaled).toInt256();
      binLpFeeAmount = token1FeeScaled - protocolFeeAmountScaled;
      return (targetPos, out0Scaled, delta0Scaled, delta1Scaled, binLpFeeAmount);
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L762-773)
```text
        if (totalIn0Scaled > state.amountSpecifiedRemainingScaled) {
          uint256 delta = currBinPos - targetPos;
          // remaining < totalIn0Scaled ⇒ ratio < 1 ⇒ scaledDelta ≤ delta ≤ currBinPos ≤ MAX_POS_BIN
          uint256 scaledDelta =
            Math.mulDiv(delta, state.amountSpecifiedRemainingScaled, totalIn0Scaled, Math.Rounding.Ceil);
          if (scaledDelta == 0) scaledDelta = 1;
          targetPos = currBinPos > scaledDelta ? currBinPos - scaledDelta : 0;

          // Rescale out1Scaled proportionally; remaining < totalIn0Scaled ⇒ result ≤ out1Scaled ≤ MAX_POS_BIN
          out1Scaled = (out1Scaled * state.amountSpecifiedRemainingScaled) / totalIn0Scaled;
          totalIn0Scaled = state.amountSpecifiedRemainingScaled;
        }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L796-800)
```text
      (int256 amount0DeltaExternal, int256 amount1DeltaExternal) =
        deltasScaledToExternal(amount0DeltaScaled, amount1DeltaScaled);
      amount0Delta = amount0DeltaExternal;
      amount1Delta = amount1DeltaExternal;
      protocolFeeAmountScaled = protocolFeeScaled;
```
