### Title
Exact-out swap notional fee incorrectly inflates `binTotals`, breaking `collectFees` accounting — (`metric-core/contracts/MetricOmmPool.sol`)

---

### Summary

In `_executeSwap`, for **exact-output** swaps, the notional fee on the input token is added to `amount0DeltaScaled` / `amount1DeltaScaled` **before** the `binTotals` update. This causes `binTotals` to be inflated by the notional fee amount, while `notionalFeeToken0Scaled` / `notionalFeeToken1Scaled` also tracks the same amount. The notional fee is double-counted: once in `binTotals` (LP-owned tokens) and once in the dedicated notional fee accumulator. The `collectFees` function then computes a spread-fee surplus that is understated by the full notional fee amount, and reverts with an arithmetic underflow whenever the notional fee exceeds the spread fee.

---

### Finding Description

**Root cause — asymmetric notional fee application in `_executeSwap`**

For **exact-in** swaps the notional fee is charged on the *output* token. The output delta is made less negative, so `binTotals` for the output token decreases by `(output − notionalFee)`. The notional fee stays in the pool and is tracked only in `notionalFeeToken*Scaled`. This is correct.

For **exact-out** swaps the notional fee is charged on the *input* token. The code adds `notionalFeeScaled` to `amount0DeltaScaled` (or `amount1DeltaScaled`) and simultaneously records it in `notionalFeeToken0Scaled` (or `notionalFeeToken1Scaled`). The `binTotals` update then uses the already-inflated delta:

```
// exact-out, zeroForOne  (lines 776-782 then 732-736)
amount0DeltaScaled = amount0DeltaScaled + int256(notionalFeeScaled);   // ← inflated
notionalFeeToken0Scaled += notionalFeeScaled;                          // ← also tracked here

binTotals.scaledToken0 =
  (uint256(binTotals.scaledToken0) + uint256(amount0DeltaScaled) - protocolFeeScaled).toUint128();
//  ↑ includes notionalFeeScaled — should not
``` [1](#0-0) [2](#0-1) 

The same defect exists for the `!zeroForOne` exact-out path: [3](#0-2) [4](#0-3) 

**How `collectFees` breaks**

`collectFees` computes the spread-fee surplus as:

```solidity
uint256 surplus0Scaled =
  balance0() * TOKEN_0_SCALE_MULTIPLIER - uint256(binTotals.scaledToken0) - notionalFee0AmountScaled;
``` [5](#0-4) 

With the bug, after an exact-out zeroForOne swap:

| Quantity | Value |
|---|---|
| `balance0() * scale` | `amountIn + notionalFee` |
| `binTotals.scaledToken0` | `amountIn + notionalFee − protocolFee` ← inflated |
| `notionalFee0AmountScaled` | `notionalFee` |
| **`surplus0Scaled`** | `protocolFee − notionalFee` ← **can underflow** |

Whenever `notionalFee > protocolFee` (spread fee), the subtraction underflows and `collectFees` reverts. Even when it does not revert, the spread fee distributed to admin and protocol is understated by exactly `notionalFee`.

**Contrast with exact-in (correct path)**

For exact-in zeroForOne the notional fee is on the output token:

```solidity
// lines 753-762
uint256 notionalFeeScaled = uint256(-amount1DeltaScaled) * notionalFeeE8 / 1e8;
amount1DeltaScaled = amount1DeltaScaled + int256(notionalFeeScaled); // less negative
notionalFeeToken1Scaled += notionalFeeScaled;
// binTotals.scaledToken1 decreases by (output − notionalFee) — correct
``` [6](#0-5) 

The notional fee is excluded from `binTotals` in this path. The exact-out path should mirror this behaviour but does not.

---

### Impact Explanation

1. **`collectFees` DoS** — After any exact-out swap with `notionalFeeE8 > 0`, `binTotals` is inflated. Once accumulated notional fees exceed accumulated spread fees, `collectFees` reverts permanently. Protocol and admin can never collect spread fees again without an upgrade.
2. **Understated spread-fee distribution** — Even before the revert threshold, every exact-out swap silently reduces the spread fee surplus by `notionalFeeScaled`. Admin and protocol receive less than their entitled share.
3. **`binTotals` / bin-state divergence** — `binTotals.scaledToken0` exceeds the sum of all `binState.token0BalanceScaled` values by the accumulated notional fee. The swap availability cap (`totalAvailableToken0Scaled = binTotals.scaledToken0`) is overstated, though actual per-bin execution is still bounded by individual bin balances.

---

### Likelihood Explanation

- Requires `notionalFeeE8 > 0` (a standard pool configuration option).
- Triggered by any caller using `swap` with a negative `amountSpecified` (exact-out mode) — a normal, unprivileged operation.
- No special state or timing is needed; the inflation accumulates monotonically with each exact-out swap.

---

### Recommendation

Apply the notional fee to the external delta **after** the `binTotals` update, or subtract `notionalFeeScaled` from the `binTotals` increment. The simplest fix is to capture the pre-notional-fee delta for the `binTotals` update:

```solidity
// In _executeSwap, exact-out zeroForOne path:
// 1. Update binTotals with the pre-notional amount0DeltaScaled
binTotals.scaledToken0 =
  (uint256(binTotals.scaledToken0) + uint256(amount0DeltaScaled) - protocolFeeScaled).toUint128();

// 2. Then apply notional fee to the external delta only
uint256 notionalFeeScaled = feeExclusiveInputScaled * notionalFeeE8 / 1e8;
if (notionalFeeScaled > 0) {
  amount0DeltaScaled = amount0DeltaScaled + int256(notionalFeeScaled);
  notionalFeeToken0Scaled += notionalFeeScaled;
}
```

Apply the same reordering to the `!zeroForOne` exact-out path.

---

### Proof of Concept

**Setup:** Pool with `notionalFeeE8 = 1_000_000` (1%), `spreadFeeE6 = 1_000` (0.1%), LP deposits 10 000 token0 above current price.

**Step 1 — Exact-out swap (buy token0 with token1):**
- `feeExclusiveInputScaled` = 1 000 (pre-fee notional)
- `notionalFeeScaled` = 1 000 × 1% = 10
- `protocolFeeScaled` (spread fee) ≈ 1 000 × 0.1% = 1
- `amount1DeltaScaled` is inflated by 10 before `binTotals` update
- `binTotals.scaledToken1` += `amountIn + 10 − 1` instead of `amountIn − 1`
- `notionalFeeToken1Scaled` = 10

**Step 2 — `collectFees`:**
```
surplus1Scaled = balance1 * scale
               − binTotals.scaledToken1   // inflated by 10
               − notionalFeeToken1Scaled  // 10
             = (amountIn + 10) − (amountIn + 10 − 1) − 10
             = 1 − 10
             = underflow → revert
```

`collectFees` reverts. Protocol and admin fees are permanently locked.

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L385-388)
```text
    uint256 surplus0Scaled =
      balance0() * TOKEN_0_SCALE_MULTIPLIER - uint256(binTotals.scaledToken0) - notionalFee0AmountScaled;
    uint256 surplus1Scaled =
      balance1() * TOKEN_1_SCALE_MULTIPLIER - uint256(binTotals.scaledToken1) - notionalFee1AmountScaled;
```

**File:** metric-core/contracts/MetricOmmPool.sol (L732-739)
```text
      if (zeroForOne) {
        // casting to uint256 is safe because amount0DeltaScaled is positive in zeroForOne flow.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken0 =
          (uint256(binTotals.scaledToken0) + uint256(amount0DeltaScaled) - protocolFeeScaled).toUint128(); // forge-lint: disable-line(unsafe-typecast)
        // casting to uint128/uint256 is safe because bin totals remain bounded by uint128-scaled accounting invariants.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken1 = uint128(uint256(binTotals.scaledToken1) - uint256(-amount1DeltaScaled));
```

**File:** metric-core/contracts/MetricOmmPool.sol (L740-748)
```text
      } else {
        // casting to uint256 is safe because amount1DeltaScaled is positive in !zeroForOne flow.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken1 =
          (uint256(binTotals.scaledToken1) + uint256(amount1DeltaScaled) - protocolFeeScaled).toUint128(); // forge-lint: disable-line(unsafe-typecast)
        // casting to uint128/uint256 is safe because bin totals remain bounded by uint128-scaled accounting invariants.
        // forge-lint: disable-next-line(unsafe-typecast)
        binTotals.scaledToken0 = uint128(uint256(binTotals.scaledToken0) - uint256(-amount0DeltaScaled));
      }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L750-762)
```text
      if (notionalFeeE8 > 0) {
        if (amountSpecified > 0) {
          // exact in: notional fee on output token
          if (zeroForOne) {
            // safe because amount1DeltaScaled is bounded by uint128 total scaled token1 in bins.
            // forge-lint: disable-next-line(unsafe-typecast)
            uint256 notionalFeeScaled = uint256(-amount1DeltaScaled) * notionalFeeE8 / 1e8;
            if (notionalFeeScaled > 0) {
              // safe because notionalFeeScaled is bounded by uint128
              // forge-lint: disable-next-line(unsafe-typecast)
              amount1DeltaScaled = amount1DeltaScaled + int256(notionalFeeScaled);
              notionalFeeToken1Scaled = (uint256(notionalFeeToken1Scaled) + notionalFeeScaled).toUint128();
            }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L776-782)
```text
          if (zeroForOne) {
            uint256 notionalFeeScaled = feeExclusiveInputScaled * notionalFeeE8 / 1e8;
            if (notionalFeeScaled > 0) {
              // safe because notionalFeeScaled is bounded by uint128
              // forge-lint: disable-next-line(unsafe-typecast)
              amount0DeltaScaled = amount0DeltaScaled + int256(notionalFeeScaled);
              notionalFeeToken0Scaled = (uint256(notionalFeeToken0Scaled) + notionalFeeScaled).toUint128();
```

**File:** metric-core/contracts/MetricOmmPool.sol (L784-793)
```text
          } else {
            uint256 notionalFeeScaled = feeExclusiveInputScaled * notionalFeeE8 / 1e8;
            if (notionalFeeScaled > 0) {
              // safe because notionalFeeScaled is bounded by uint128
              // forge-lint: disable-next-line(unsafe-typecast)
              amount1DeltaScaled = amount1DeltaScaled + int256(notionalFeeScaled);
              notionalFeeToken1Scaled = (uint256(notionalFeeToken1Scaled) + notionalFeeScaled).toUint128();
            }
          }
        }
```
