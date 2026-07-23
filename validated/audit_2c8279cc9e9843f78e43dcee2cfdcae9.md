### Title
JIT Liquidity Front-Running Enables LP Fee Siphoning Without Equivalent Risk - (File: `metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

The LP fee distribution mechanism in Metric OMM embeds earned fees directly into bin token balances at swap time, distributed proportionally to all current LPs with no minimum holding period or time-weighted accounting. An attacker can front-run large swaps by adding liquidity just before execution, capture a proportional share of the LP fees, and immediately remove liquidity — siphoning fees from long-term LPs who bore the actual market risk.

---

### Finding Description

**Root cause — proportional-at-snapshot fee embedding:**

In `LiquidityLib.addLiquidity`, when a bin already has liquidity (`binTotalSharesVal > 0`), new shares are priced proportionally to the *current* bin balance snapshot: [1](#0-0) 

```solidity
amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
```

When a swap executes, the LP fee (the portion of input token exceeding the fair oracle price) is added **directly** into the bin's token balance inside `SwapMath.buyToken0InBinSpecifiedIn`: [2](#0-1) 

```solidity
binState.token0BalanceScaled -= out0Scaled.toUint104();
binState.token1BalanceScaled =
  uint256((binState.token1BalanceScaled) + totalIn1Scaled - protocolFeeAmountScaled).toUint104();
```

The same pattern applies in `buyToken1InBinSpecifiedIn`, `buyToken0InBinSpecifiedOut`, and `buyToken1InBinSpecifiedOut`. [3](#0-2) 

When `removeLiquidity` is called, the LP receives their proportional share of the *post-swap* bin balance (floor division): [4](#0-3) 

```solidity
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

There is **no minimum holding period**, **no lock**, and **no time-weighted fee accounting** anywhere in the liquidity path.

<cite repo="Tylerpinwa/2026-07-metric-dev-

### Citations

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L109-110)
```text
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L205-206)
```text
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

**File:** metric-core/contracts/libraries/SwapMath.sol (L636-650)
```text
      uint256 token1FeeScaled = lpFeeScaledFromGrossInput(totalIn1Scaled, currBinBuyFeeX64, onePlusBuyFeeX64);

      uint256 protocolFeeAmountScaled = (token1FeeScaled * spreadFeeE6) / 1e6;
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
