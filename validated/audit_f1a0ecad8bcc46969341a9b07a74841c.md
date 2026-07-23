### Title
`LiquidityLib.addLiquidity` accepts zero-token deposits into swap-drained bins, diluting existing LP claims on future bin income — (`File: metric-core/contracts/libraries/LiquidityLib.sol`)

---

### Summary

When a swap fully drains a bin's token balances to zero, `binTotalShares[binIdx]` is never updated by the swap path. A subsequent `addLiquidity` call on that bin takes the proportional branch (because `binTotalSharesVal != 0`) and computes a required deposit of exactly zero tokens, yet still mints shares and increments `binTotalShares`. The attacker pays nothing and receives a proportional claim on all future tokens that enter the bin, directly diluting the original LP's recoverable principal.

---

### Finding Description

The swap execution path in `MetricOmmPool` updates only `binState.token0BalanceScaled` and `binState.token1BalanceScaled` (via `SwapMath`). It never touches `_binTotalShares[binIdx]`. This is confirmed by the test assertion: *"Shares should not change during swap."* [1](#0-0) 

After a swap fully crosses a bin, the bin reaches the state:

```
binState.token0BalanceScaled == 0
binState.token1BalanceScaled == 0
_binTotalShares[binIdx]      == N   (original LP's shares, unchanged)
```

When `addLiquidity` is subsequently called on this bin, the branch selector is:

```solidity
if (binTotalSharesVal == 0) {
    // fresh-bin path — uses initialScaledToken*PerShareE18
} else {
    amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
    amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
}
``` [2](#0-1) 

Because `binTotalSharesVal != 0`, the proportional branch is taken. With both balances at zero:

```
amount0Scaled = ceil(0 * sharesToAdd / N) = 0
amount1Scaled = ceil(0 * sharesToAdd / N) = 0
```

The callback guard then skips payment entirely:

```solidity
if (amount0Added > 0 || amount1Added > 0) {
    // callback — skipped
}
``` [3](#0-2) 

Yet shares and total shares are unconditionally written:

```solidity
binTotalShares[binIdx] = binTotalSharesVal + sharesToAdd;
positionBinShares[posKey] = newUserShares;
``` [4](#0-3) 

The attacker now holds `sharesToAdd / (N + sharesToAdd)` of the bin. When a reverse swap later deposits tokens into that bin, the attacker's free shares entitle them to a proportional withdrawal, directly reducing what the original LP can recover.

---

### Impact Explanation

**Direct loss of LP principal.** The original LP deposited real tokens and holds shares representing a 100% claim on the bin's future income. After the attack, their claim is diluted to `N / (N + sharesToAdd)`. The attacker extracts the difference — real tokens — at zero cost. This is a permanent, unconditional transfer of value from the original LP to the attacker on every subsequent reverse swap that refills the bin.

The `removeLiquidity` path confirms the loss: it computes withdrawable amounts as `binState.token*BalanceScaled * userShares / binTotalSharesVal`, so the diluted denominator directly reduces the original LP's payout. [5](#0-4) 

---

### Likelihood Explanation

**High.** Bin draining is a routine consequence of normal swap activity — any swap large enough to cross a bin fully produces the vulnerable state. No privileged access is required; `addLiquidity` is a public, permissionless function callable by any address. The only constraint is that `sharesToAdd >= minimalMintableLiquidity`, which is a pool-configured constant that any attacker can satisfy. The attack is repeatable across every bin and every pool. [6](#0-5) 

---

### Recommendation

In `LiquidityLib.addLiquidity`, add a guard that detects the insolvent-bin state (non-zero total shares, zero token balances) and redirects to the fresh-bin pricing path:

```solidity
if (binTotalSharesVal == 0
    || (binState.token0BalanceScaled == 0 && binState.token1BalanceScaled == 0))
{
    // use initialScaledToken*PerShareE18 pricing
} else {
    amount0Scaled = Math.ceilDiv(...);
    amount1Scaled = Math.ceilDiv(...);
}
```

Alternatively, the swap path should reset `_binTotalShares[binIdx]` to zero whenever a bin is fully drained (both balances reach zero), analogous to Ajna's `BucketBankruptcy` flag. This ensures the next depositor always pays the canonical initial price per share rather than inheriting a free claim. [2](#0-1) 

---

### Proof of Concept

```
Setup:
  - Pool with bins [-1, 0, 1, 2, 3, 4, 5]; curBinIdx = 0
  - LP1 calls addLiquidity(bin=4, shares=10_000)
    → deposits token0 (bin 4 is above cursor)
    → binTotalShares[4] = 10_000
    → binState[4].token0BalanceScaled = X (e.g. 10_000 scaled units)

Step 1 — Drain bin 4 via swap:
  - Swapper calls swap(zeroForOne=false, largeAmount)
    → cursor advances through bins 1,2,3,4
    → binState[4].token0BalanceScaled = 0
    → binState[4].token1BalanceScaled = 0
    → binTotalShares[4] = 10_000  ← UNCHANGED

Step 2 — Attacker mints free shares:
  - Attacker calls addLiquidity(bin=4, shares=10_000)
    → binTotalSharesVal = 10_000 ≠ 0 → proportional branch
    → amount0Scaled = ceil(0 * 10_000 / 10_000) = 0
    → amount1Scaled = 0
    → callback skipped (no payment)
    → binTotalShares[4] = 20_000
    → positionBinShares[attacker][4] = 10_000

Step 3 — Reverse swap refills bin 4:
  - Another swapper calls swap(zeroForOne=true)
    → cursor moves back through bin 4
    → binState[4].token0BalanceScaled = Y (new tokens enter)

Step 4 — Attacker withdraws:
  - Attacker calls removeLiquidity(bin=4, shares=10_000)
    → receives Y * 10_000 / 20_000 = Y/2 token0
    → paid zero to acquire these shares

Step 5 — LP1 loss:
  - LP1 calls removeLiquidity(bin=4, shares=10_000)
    → receives Y * 10_000 / 20_000 = Y/2 token0
    → expected Y/1 = Y (100% of bin)
    → loss = Y/2 tokens transferred to attacker for free
```

### Citations

**File:** metric-core/test/MetricOmmPool.swap.t.sol (L218-219)
```text
    // Shares should not change during swap
    assertEq(sharesAfter, sharesBefore, "Shares should not change during swap");
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L85-111)
```text
          if (binTotalSharesVal == 0) {
            if (binIdx < curBinIdxCache) {
              amount1Scaled = Math.ceilDiv(_checkedMul(ctx.initialScaledToken1PerShareE18, sharesToAdd), 1e18);
            } else if (binIdx > curBinIdxCache) {
              amount0Scaled = Math.ceilDiv(_checkedMul(ctx.initialScaledToken0PerShareE18, sharesToAdd), 1e18);
            } else {
              uint256 token0Proportion = type(uint104).max - ctx.curPosInBin;
              uint256 token1Proportion = ctx.curPosInBin;
              amount0Scaled =
              (Math.mulDiv(
                  token0Proportion * ctx.initialScaledToken0PerShareE18,
                  sharesToAdd,
                  uint256(type(uint104).max) * 1e18,
                  Math.Rounding.Ceil
                ));
              amount1Scaled =
              (Math.mulDiv(
                  token1Proportion * ctx.initialScaledToken1PerShareE18,
                  sharesToAdd,
                  uint256(type(uint104).max) * 1e18,
                  Math.Rounding.Ceil
                ));
            }
          } else {
            amount0Scaled = Math.ceilDiv(_checkedMul(binState.token0BalanceScaled, sharesToAdd), binTotalSharesVal);
            amount1Scaled = Math.ceilDiv(_checkedMul(binState.token1BalanceScaled, sharesToAdd), binTotalSharesVal);
          }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L120-121)
```text
          binTotalShares[binIdx] = binTotalSharesVal + sharesToAdd;
          positionBinShares[posKey] = newUserShares;
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L144-155)
```text
      if (amount0Added > 0 || amount1Added > 0) {
        uint256 balance0Before = IERC20(ctx.token0).balanceOf(address(this));
        uint256 balance1Before = IERC20(ctx.token1).balanceOf(address(this));
        IMetricOmmModifyLiquidityCallback(msg.sender)
          .metricOmmModifyLiquidityCallback(amount0Added, amount1Added, callbackData);
        if (amount0Added > 0 && balance0Before + amount0Added > IERC20(ctx.token0).balanceOf(address(this))) {
          revert IMetricOmmPoolActions.InsufficientTokenBalance();
        }
        if (amount1Added > 0 && balance1Before + amount1Added > IERC20(ctx.token1).balanceOf(address(this))) {
          revert IMetricOmmPoolActions.InsufficientTokenBalance();
        }
      }
```

**File:** metric-core/contracts/libraries/LiquidityLib.sol (L205-206)
```text
          uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
          uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L182-196)
```text
  function addLiquidity(
    address owner,
    uint80 salt,
    LiquidityDelta calldata deltas,
    bytes calldata callbackData,
    bytes calldata extensionData
  ) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (uint256 amount0Added, uint256 amount1Added) {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    _beforeAddLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Added, amount1Added) = LiquidityLib.addLiquidity(
      _liquidityContext(), owner, salt, deltas, callbackData, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterAddLiquidity(msg.sender, owner, salt, deltas, amount0Added, amount1Added, extensionData);
  }
```
