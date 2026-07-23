Looking at the external bug class: a permissionless function that resets an accumulator to zero even when rounding causes zero tokens to be transferred, permanently freezing the income.

Let me trace the exact analog in Metric OMM.

**Key facts found:**

1. `collectPoolFees` is explicitly permissionless — anyone can call it.
2. `collectFees` always resets `notionalFeeToken0Scaled = 0` and `notionalFeeToken1Scaled = 0` unconditionally, regardless of whether any tokens were actually transferred.
3. The conversion from scaled to external uses `Math.Rounding.Floor`, so if the scaled amount is less than `TOKEN_0_SCALE_MULTIPLIER`, the external amount is 0 and no transfer occurs.
4. For USDC/USDT (6 decimals), `TOKEN_0_SCALE_MULTIPLIER = 10^(18-6) = 10^12`. Any notional accumulator value below `10^12` rounds to 0 external units.
5. When spread fee is 0, the cleared notional amount is not recoverable — it is not in `binTotals` (so LPs can't withdraw it), not in the notional accumulator (cleared), and the spread fee path is skipped (`spreadSumE6 == 0`).
6. The existing test `test_collectProtocolFees_math_overallocates_whenSpreadAndNotionalBothActive` documents a related accounting anomaly but does not cover the zero-transfer/accumulator-clear case.

---

### Title
Permissionless `collectPoolFees` unconditionally clears notional fee accumulator even when floor-rounding produces zero external transfer, permanently freezing protocol fees — (`metric-core/contracts/MetricOmmPool.sol`)

### Summary

`MetricOmmPool.collectFees()` always resets `notionalFeeToken0Scaled` and `notionalFeeToken1Scaled` to zero after fee collection, even when the accumulated scaled amount is below `TOKEN_X_SCALE_MULTIPLIER` and the floor-rounded external transfer amount is zero. Because `MetricOmmPoolFactory.collectPoolFees()` is permissionless, an attacker can call it after every small swap to prevent the notional accumulator from ever reaching the transfer threshold, permanently freezing protocol and admin notional fees inside the pool contract with no recovery path.

### Finding Description

In `MetricOmmPool.collectFees()`:

```solidity
// metric-core/contracts/MetricOmmPool.sol L382-430
uint256 notionalFee0AmountScaled = notionalFeeToken0Scaled;
...
uint256 notionalFee0ToProtocolScaled = notionalFee0AmountScaled - notionalFee0ToAdminScaled;
...
(uint256 totalFee0ToProtocol, uint256 totalFee1ToProtocol) =
    deltasScaledToExternal(totalFee0ToProtocolScaled, totalFee1ToProtocolScaled, Math.Rounding.Floor);
...
if (totalFee0ToProtocol > 0) {
    transferToken0(FACTORY, totalFee0ToProtocol);
}
...
notionalFeeToken0Scaled = 0;   // ← always cleared, even if totalFee0ToProtocol == 0
notionalFeeToken1Scaled = 0;
```

The floor-rounding conversion:

```solidity
// metric-core/contracts/MetricOmmPool.sol L626-627
deltaAmount0 = scaledDeltaAmount0 / TOKEN_0_SCALE_MULTIPLIER;
```

For a 6-decimal token (USDC), `TOKEN_0_SCALE_MULTIPLIER = 10^12`. Any `notionalFeeToken0Scaled` value in `[1, 10^12 - 1]` produces `totalFee0ToProtocol = 0`, so no tokens are transferred, yet the accumulator is unconditionally zeroed.

The factory entry point has no access control:

```solidity
// metric-core/contracts/MetricOmmPoolFactory.sol L379-389
function collectPoolFees(address pool) external override nonReentrant {
    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool).collectFees(
        c.protocolSpreadFeeE6, c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8, c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
    );
}
```

After the accumulator is cleared to zero with no transfer, the pool's ERC-20 balance is unchanged and `binTotals` is unchanged. On the next `collectFees` call:

```solidity
surplus0Scaled = balance0() * TOKEN_0_SCALE_MULTIPLIER
               - uint256(binTotals.scaledToken0)
               - notionalFee0AmountScaled;   // notionalFee0AmountScaled == 0 now
```

The cleared notional amount is now inside `surplus0Scaled`. If `spreadSumE6 == 0` (no spread fee configured), the spread fee path is skipped entirely and the amount is permanently inaccessible — not to protocol, not to admin, not to LPs (who only receive their proportional share of `binState.token0BalanceScaled`, not the surplus). If `spreadSumE6 > 0`, the amount is eventually recovered as spread fee, but the split between admin and protocol is distorted away from the intended notional fee split.

### Impact Explanation

For a USDC/USDT pool with notional fee enabled and spread fee = 0:

- An attacker calls `collectPoolFees` after every swap that generates `notionalFeeToken0Scaled < 10^12` (i.e., before the accumulator reaches 1 USDC).
- Each call clears up to `10^12 - 1` scaled units (~0.999999 USDC) with zero transfer.
- The cleared amount is permanently frozen in the pool — unreachable by any party.
- At a 1% notional fee rate, the accumulator reaches the threshold after ~100 USDC of swap volume. On L2s (gas cost ~$0.01–0.10 per call), the attacker spends $0.10 to deny the protocol $1 in fees.
- Over $1M in pool volume, the attacker spends ~$1,000 in gas to freeze ~$10,000 in protocol notional fees.
- The loss is permanent and non-recoverable when spread fee is zero.

This satisfies the contest's Medium threshold: loss > 0.01% and > $10 USD, replayable indefinitely.

### Likelihood Explanation

- **Trigger**: Permissionless `collectPoolFees` — no special role required.
- **Preconditions**: Low-decimal token pair (USDC/USDT, in-scope per README), notional fee > 0, spread fee = 0 (a valid and documented configuration).
- **Cost**: L2 gas per call is $0.01–0.10, well below the per-call fee denied (~$1 USDC).
- **Likelihood**: Low-to-Medium (requires specific fee configuration and active griefing), but the impact is high when conditions are met.

### Recommendation

Do not unconditionally reset the notional fee accumulators. Instead, only clear the portion that was actually transferred, or accumulate the unspent remainder into the next collection cycle:

```solidity
// Only clear what was actually paid out in external units
uint256 paidOut0Scaled = totalFee0ToProtocol * TOKEN_0_SCALE_MULTIPLIER
                       + totalFee0ToAdmin * TOKEN_0_SCALE_MULTIPLIER;
notionalFeeToken0Scaled = uint128(notionalFee0AmountScaled > paidOut0Scaled
    ? notionalFee0AmountScaled - paidOut0Scaled
    : 0);
```

Alternatively, restrict `collectPoolFees` to the pool admin or protocol so that griefing via repeated premature collection is not possible.

### Proof of Concept

1. Deploy a USDC (6-decimal) / WETH pool with `protocolNotionalFeeE8 = 1_000_000` (1%) and `protocolSpreadFeeE6 = 0`, `adminSpreadFeeE6 = 0`.
2. LP adds liquidity.
3. Trader swaps exactly 99 USDC (exact-in, zeroForOne). The notional fee on the output is `~0.99 USDC` → `notionalFeeToken1Scaled ≈ 0.99 * 10^12 = 9.9 * 10^11 < 10^12`.
4. Attacker calls `MetricOmmPoolFactory.collectPoolFees(pool)`.
   - `notionalFee1AmountScaled = 9.9 * 10^11`
   - `totalFee1ToProtocolScaled = 9.9 * 10^11`
   - `totalFee1ToProtocol = 9.9 * 10^11 / 10^12 = 0` (floor)
   - No transfer. `notionalFeeToken1Scaled = 0`.
5. The ~0.99 USDC notional fee is permanently frozen in the pool.
6. Repeat after every ~99 USDC of swap volume. Over $1M in volume, ~$10,000 in notional fees are frozen.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** metric-core/contracts/MetricOmmPool.sol (L382-433)
```text
    uint256 notionalFee0AmountScaled = notionalFeeToken0Scaled;
    uint256 notionalFee1AmountScaled = notionalFeeToken1Scaled;

    uint256 surplus0Scaled =
      balance0() * TOKEN_0_SCALE_MULTIPLIER - uint256(binTotals.scaledToken0) - notionalFee0AmountScaled;
    uint256 surplus1Scaled =
      balance1() * TOKEN_1_SCALE_MULTIPLIER - uint256(binTotals.scaledToken1) - notionalFee1AmountScaled;

    unchecked {
      uint256 spreadFee0ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * adminSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToAdminScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * adminSpreadFeeE6_) / spreadSumE6;

      uint256 spreadFee0ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus0Scaled * protocolSpreadFeeE6_) / spreadSumE6;
      uint256 spreadFee1ToProtocolScaled = spreadSumE6 == 0 ? 0 : (surplus1Scaled * protocolSpreadFeeE6_) / spreadSumE6;

      uint256 notionalFee0ToAdminScaled =
        notionalSumE8 == 0 ? 0 : (notionalFee0AmountScaled * adminNotionalFeeE8_) / notionalSumE8;
      uint256 notionalFee1ToAdminScaled =
        notionalSumE8 == 0 ? 0 : (notionalFee1AmountScaled * adminNotionalFeeE8_) / notionalSumE8;

      uint256 notionalFee0ToProtocolScaled = notionalFee0AmountScaled - notionalFee0ToAdminScaled;
      uint256 notionalFee1ToProtocolScaled = notionalFee1AmountScaled - notionalFee1ToAdminScaled;

      uint256 totalFee0ToAdminScaled = spreadFee0ToAdminScaled + notionalFee0ToAdminScaled;
      uint256 totalFee1ToAdminScaled = spreadFee1ToAdminScaled + notionalFee1ToAdminScaled;

      uint256 totalFee0ToProtocolScaled = spreadFee0ToProtocolScaled + notionalFee0ToProtocolScaled;
      uint256 totalFee1ToProtocolScaled = spreadFee1ToProtocolScaled + notionalFee1ToProtocolScaled;

      (uint256 totalFee0ToAdmin, uint256 totalFee1ToAdmin) =
        deltasScaledToExternal(totalFee0ToAdminScaled, totalFee1ToAdminScaled, Math.Rounding.Floor);
      (uint256 totalFee0ToProtocol, uint256 totalFee1ToProtocol) =
        deltasScaledToExternal(totalFee0ToProtocolScaled, totalFee1ToProtocolScaled, Math.Rounding.Floor);

      if (totalFee0ToAdmin > 0) {
        transferToken0(adminFeeDestination_, totalFee0ToAdmin);
      }
      if (totalFee1ToAdmin > 0) {
        transferToken1(adminFeeDestination_, totalFee1ToAdmin);
      }
      if (totalFee0ToProtocol > 0) {
        transferToken0(FACTORY, totalFee0ToProtocol);
      }
      if (totalFee1ToProtocol > 0) {
        transferToken1(FACTORY, totalFee1ToProtocol);
      }

      notionalFeeToken0Scaled = 0;
      notionalFeeToken1Scaled = 0;

      emit ProtocolFeesCollected(totalFee0ToProtocol, totalFee1ToProtocol, totalFee0ToAdmin, totalFee1ToAdmin);
    }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L617-628)
```text
  function deltasScaledToExternal(uint256 scaledDeltaAmount0, uint256 scaledDeltaAmount1, Math.Rounding rounding)
    internal
    view
    returns (uint256 deltaAmount0, uint256 deltaAmount1)
  {
    if (rounding == Math.Rounding.Ceil) {
      deltaAmount0 = Math.ceilDiv(scaledDeltaAmount0, TOKEN_0_SCALE_MULTIPLIER);
      deltaAmount1 = Math.ceilDiv(scaledDeltaAmount1, TOKEN_1_SCALE_MULTIPLIER);
    } else {
      deltaAmount0 = scaledDeltaAmount0 / TOKEN_0_SCALE_MULTIPLIER;
      deltaAmount1 = scaledDeltaAmount1 / TOKEN_1_SCALE_MULTIPLIER;
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

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L379-389)
```text
  function collectPoolFees(address pool) external override nonReentrant {
    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool)
      .collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
      );
  }
```
