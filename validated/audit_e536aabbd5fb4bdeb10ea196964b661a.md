### Title
LP Fee Sandwich Attack via Instant Liquidity Add/Remove — (File: metric-core/contracts/libraries/LiquidityLib.sol)

---

### Summary

LP fees from swaps are added directly to per-bin token balances (`binState.token0BalanceScaled` / `binState.token1BalanceScaled`). Because `addLiquidity` and `removeLiquidity` have no time-lock, cooldown, or per-share fee-growth checkpoint, an attacker can sandwich any large swap visible in the public mempool: add a dominant share position before the swap, let the swap deposit LP fees into the bin, then immediately remove the position and extract a proportional share of those fees. Existing LPs lose the fees they earned.

---

### Finding Description

**Fee accumulation mechanism**

In `SwapMath.buyToken0InBinSpecifiedIn`, the LP fee (gross input minus protocol fee) is added directly to the bin's token balance:

```solidity
// SwapMath.sol lines 639–641
binState.token0BalanceScaled -= out0Scaled.toUint104();
binState.token1BalanceScaled =
    uint256((binState.token1BalanceScaled) + totalIn1Scaled - protocolFeeAmountScaled).toUint104();
```

`totalIn1Scaled` includes the LP fee (`token1FeeScaled`). After the swap, `binState.token1BalanceScaled` is permanently higher by `lpFee = token1FeeScaled - protocolFeeAmountScaled`. The same pattern applies in `buyToken1InBinSpecifiedIn`, `buyToken0InBinSpecifiedOut`, and `buyToken1InBinSpecifiedOut`.

**Share-proportional withdrawal**

`removeLiquidity` pays out strictly proportional to the current bin balance:

```solidity
// LiquidityLib.sol lines 205–206
uint256 amount0Scaled = _checkedMul(binState.token0BalanceScaled, sharesToRemove) / binTotalSharesVal;
uint256 amount1Scaled = _checkedMul(binState.token1BalanceScaled, sharesToRemove) / binTotalSharesVal;
```

**No time-lock or fee-growth checkpoint**

`addLiquidity` carries no `whenNotPaused` guard and no minimum holding period:

```solidity
// MetricOmmPool.sol lines 182–196
function addLiquidity(...) external nonReentrant(PoolActions.ADD_LIQUIDITY) returns (...) {
```

`removeLiquidity` only checks `msg.sender == owner`:

```solidity
// MetricOmmPool.sol line 206
if (msg.sender != owner) revert NotPositionOwner();
```

There is no per-share fee-growth accumulator (unlike Uniswap v3's `feeGrowthInside`). Any shares minted before a swap immediately entitle the holder to a proportional share of fees deposited by that swap.

**Attack flow**

Let the target bin have `B1` token1, total shares `S`, and an incoming swap that will deposit LP fee `F` into token1.

1. **Front-run** — attacker calls `addLiquidity` with `s` shares. Cost (ceiling): `B1 * s / S` token1. New bin state: `B1 * (S+s)/S` token1, total shares `S+s`.
2. **Swap executes** — LP fee `F` is added. Bin now holds `B1*(S+s)/S + F` token1.
3. **Back-run** — attacker calls `removeLiquidity` with `s` shares. Receives (floor): `(B1*(S+s)/S + F) * s/(S+s)` token1 = `B1*s/S + F*s/(S+s)`.
4. **Attacker profit** ≈ `F * s/(S+s)` (ceiling rounding on entry is at most 1 wei per bin, negligible).

With sufficient capital (`s >> S`), the attacker captures nearly 100 % of `F`. Existing LPs receive only `F * S/(S+s)` instead of `F`.

---

### Impact Explanation

Direct, quantifiable loss of LP fee revenue for all existing liquidity providers in the sandwiched bin. The attacker extracts real token balances (`token1BalanceScaled` or `token0BalanceScaled`) that were credited to the pool by a legitimate swap. Pool solvency is not broken, but LP claims are diluted: the bin balance covers all shares, but the fee portion that should accrue to long-term LPs is captured by the sandwich. This is a Critical/High loss of owed LP assets above Sherlock thresholds.

---

### Likelihood Explanation

High. Any large swap broadcast to a public mempool is exploitable. The attacker needs only:
- Capital to add liquidity (no special role or permission).
- A standard flashbots bundle or priority-fee front/back-run.
- No reentrancy (three separate transactions in one block suffice).

The `MINIMAL_MINTABLE_LIQUIDITY` floor is a dust guard, not a meaningful barrier. The extension system (`_beforeAddLiquidity` / `_afterAddLiquidity`) can optionally gate deposits, but no such extension is deployed by default and the core pool imposes none.

---

### Recommendation

1. **Per-share fee-growth checkpoint** (preferred): Track a `feeGrowthInside` accumulator per bin (analogous to Uniswap v3). Credit fees to a snapshot at the time of minting; only fees accumulated *after* a position is opened are claimable by that position. This eliminates the sandwich entirely.

2. **Minimum holding period / withdrawal delay**: Enforce a block-number or timestamp lock on newly minted positions before `removeLiquidity` is callable. This raises the cost and risk of the attack but does not eliminate it.

3. **Private mempool for large swaps**: Advise integrators to route large swaps through private relays (Flashbots Protect, MEV Blocker) to prevent front-running visibility.

---

### Proof of Concept

```
Setup:
  Bin 0 has: token0Balance = 1_000_000 (scaled), token1Balance = 1_000_000 (scaled)
  Total shares S = 1_000_000
  Existing LP holds all S shares.
  Incoming swap: trader sends 500_000 token1 → receives token0.
  LP fee rate: 0.3% → lpFee F ≈ 1_500 token1 (scaled) stays in bin.

Step 1 — Attacker front-runs addLiquidity(bin=0, shares=s=9_000_000):
  Cost (ceiling): 1_000_000 * 9_000_000 / 1_000_000 = 9_000_000 token1 (scaled)
  New bin token1: 10_000_000 (scaled), total shares: 10_000_000

Step 2 — Swap executes:
  Bin token1 becomes: 10_000_000 + 1_500 = 10_001_500 (scaled)

Step 3 — Attacker back-runs removeLiquidity(bin=0, shares=9_000_000):
  Receives (floor): 10_001_500 * 9_000_000 / 10_000_000 = 9_001_350 token1 (scaled)
  Attacker profit: 9_001_350 − 9_000_000 = 1_350 token1 (scaled)
  (= F * s/(S+s) = 1_500 * 9/10 = 1_350 ✓)

Existing LP receives only:
  10_001_500 * 1_000_000 / 10_000_000 = 1_000_150 token1 (scaled)
  Fee captured: 150 instead of 1_500 — 90% stolen.
```

**Relevant code locations:**

- Fee deposited into bin: [1](#0-0) 
- LP fee computed and split: [2](#0-1) 
- Share-proportional withdrawal (no fee checkpoint): [3](#0-2) 
- `addLiquidity` — no time-lock, no `whenNotPaused`: [4](#0-3) 
- `removeLiquidity` — only owner check, no holding period: [5](#0-4) 
- Proportional entry price (ceiling, not a meaningful barrier): [6](#0-5)

### Citations

**File:** metric-core/contracts/libraries/SwapMath.sol (L636-649)
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
```

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

**File:** metric-core/contracts/MetricOmmPool.sol (L199-212)
```text
  function removeLiquidity(address owner, uint80 salt, LiquidityDelta calldata deltas, bytes calldata extensionData)
    external
    nonReentrant(PoolActions.REMOVE_LIQUIDITY)
    returns (uint256 amount0Removed, uint256 amount1Removed)
  {
    if (deltas.binIdxs.length == 0) return (0, 0);
    if (deltas.binIdxs.length != deltas.shares.length) revert LiquidityDeltaLengthMismatch();
    if (msg.sender != owner) revert NotPositionOwner();
    _beforeRemoveLiquidity(msg.sender, owner, salt, deltas, extensionData);
    (amount0Removed, amount1Removed) = LiquidityLib.removeLiquidity(
      _liquidityContext(), owner, salt, deltas, binTotals, _binStates, _binTotalShares, _positionBinShares
    );
    _afterRemoveLiquidity(msg.sender, owner, salt, deltas, amount0Removed, amount1Removed, extensionData);
  }
```
