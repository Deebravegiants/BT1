### Title
Pool Admin Can Immediately Raise Swap Fees Without Timelock, Enabling Frontrunning of Traders — (`metric-core/contracts/MetricOmmPoolFactory.sol`)

---

### Summary

`setPoolAdminFees` allows the pool admin to instantly update `adminNotionalFeeE8` (up to 1%) and `adminSpreadFeeE6` (up to 20%) with no delay. The same admin role is required to use a timelock when rotating the price provider, proving the protocol does not fully trust the pool admin. The absence of a matching timelock on fee changes lets the pool admin frontrun any pending swap, extracting additional value from traders without warning.

---

### Finding Description

`MetricOmmPoolFactory.setPoolAdminFees` (lines 408–435) updates both fee components and immediately pushes the new totals into the pool via `setPoolFees`:

```solidity
// MetricOmmPoolFactory.sol lines 408-435
function setPoolAdminFees(address pool, uint24 newAdminSpreadFeeE6, uint24 newAdminNotionalFeeE8)
    external override nonReentrant onlyPoolAdmin(pool)
{
    if (newAdminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    if (newAdminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();
    ...
    IMetricOmmPoolFactoryActions(pool)
        .setPoolFees(c.protocolSpreadFeeE6 + c.adminSpreadFeeE6,
                     c.protocolNotionalFeeE8 + c.adminNotionalFeeE8);
}
```

The pool stores the new `notionalFeeE8` immediately and applies it to every subsequent swap in `_executeSwap`:

```solidity
// MetricOmmPool.sol lines 756-761
uint256 notionalFeeScaled = uint256(-amount1DeltaScaled) * notionalFeeE8 / 1e8;
if (notionalFeeScaled > 0) {
    amount1DeltaScaled = amount1DeltaScaled + int256(notionalFeeScaled);
    notionalFeeToken1Scaled = (uint256(notionalFeeToken1Scaled) + notionalFeeScaled).toUint128();
}
```

The hard caps are:

```solidity
// MetricOmmPoolFactory.sol lines 44-45
uint24 internal constant HARD_MAX_SPREAD_FEE_E6  = 200_000;   // 20 %
uint24 internal constant HARD_MAX_NOTIONAL_FEE_E8 = 1_000_000; //  1 %
```

By contrast, the price-provider rotation — a less financially sensitive operation — is protected by a mandatory timelock:

```solidity
// MetricOmmPoolFactory.sol lines 487-490
uint256 executeAfter = block.timestamp + timelock;
pendingPriceProvider[pool] = newPriceProvider;
pendingPriceProviderExecuteAfter[pool] = executeAfter;
```

and enforced at execution:

```solidity
// MetricOmmPoolFactory.sol lines 498-499
if (block.timestamp < execAfter) revert PriceProviderTimelockNotElapsed(execAfter, block.timestamp);
```

No equivalent pending/execute pattern exists for `setPoolAdminFees` or `setPoolBinAdditionalFees`. The per-bin additional fees (`addFeeBuyE6`, `addFeeSellE6`) are also uncapped beyond the `uint16` type limit (≈ 6.55 % in E6 units) and are applied directly to swap prices in `getSellAndBuyPrices`:

```solidity
// MetricOmmPool.sol lines 540-541
uint256 buyFeeX64  = baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6,  ONE_X64, 1e6);
uint256 sellFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeSellE6, ONE_X64, 1e6);
```

---

### Impact Explanation

A pool admin who observes a large pending swap in the mempool can atomically:

1. Call `setPoolAdminFees(pool, maxAdminSpreadFeeE6, maxAdminNotionalFeeE8)` — raising the notional fee from 0 → 1 % and the spread-fee split to 20 %.
2. Optionally call `setPoolBinAdditionalFees` on the active bin to add up to ≈ 6.55 % additional buy/sell fee.

The trader's transaction then executes at the elevated fee, paying materially more than the fee visible at submission time. The excess flows to the admin's fee destination. This is a direct, quantifiable loss of trader principal with no recourse.

---

### Likelihood Explanation

The pool admin is a semi-trusted role: the protocol already distrusts it enough to require a timelock for price-provider changes. Any pool admin — including one who turns adversarial after attracting liquidity — can execute this attack on any public mempool chain. No special setup or malicious initial configuration is required; the attack uses only the legitimately granted `setPoolAdminFees` and `setPoolBinAdditionalFees` entry points.

---

### Recommendation

Apply the same two-step, timelock-gated pattern used for price-provider rotation to all fee-raising operations:

1. Add `proposeFeeUpdate(pool, newAdminSpreadFeeE6, newAdminNotionalFeeE8)` that records the proposed values and an `executeAfter = block.timestamp + feeTimelock`.
2. Add `executeFeeUpdate(pool)` that enforces `block.timestamp >= executeAfter` before calling `setPoolFees`.
3. Apply the same pattern to `setPoolBinAdditionalFees`.

This gives LPs and traders a window to exit before a fee increase takes effect, matching the protection already afforded by the price-provider timelock.

---

### Proof of Concept

```
Setup:
  pool created with adminNotionalFeeE8 = 0, adminSpreadFeeE6 = 0
  trader submits swap: sell 100 000 USDC for token1 (large notional)

Attack:
  1. Pool admin sees the swap in the mempool.
  2. Pool admin calls:
       factory.setPoolAdminFees(pool, 200_000, 1_000_000)
     This sets notionalFeeE8 = protocolNotionalFeeE8 + 1_000_000 in the pool.
  3. Admin's tx is included first (higher gas or private relay).
  4. Trader's swap executes; _executeSwap charges:
       notionalFeeScaled = amountOut * 1_000_000 / 1e8  =  amountOut * 1 %
     The trader receives 1 % less token1 than quoted at submission time.
  5. Admin calls collectPoolFees; the 1 % notional fee flows to adminFeeDestination.

Result: trader loses ~1 % of swap output with no on-chain warning or recourse.
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L44-45)
```text
  uint24 internal constant HARD_MAX_SPREAD_FEE_E6 = 200_000;
  uint24 internal constant HARD_MAX_NOTIONAL_FEE_E8 = 1_000_000;
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L408-435)
```text
  function setPoolAdminFees(address pool, uint24 newAdminSpreadFeeE6, uint24 newAdminNotionalFeeE8)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
  {
    if (newAdminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    if (newAdminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();

    PoolFeeConfig memory c = poolFeeConfig[pool];
    IMetricOmmPoolCollectFees(pool)
      .collectFees(
        c.protocolSpreadFeeE6,
        c.adminSpreadFeeE6,
        c.protocolNotionalFeeE8,
        c.adminNotionalFeeE8,
        poolAdminFeeDestination[pool]
      );

    c.adminSpreadFeeE6 = newAdminSpreadFeeE6;
    c.adminNotionalFeeE8 = newAdminNotionalFeeE8;
    poolFeeConfig[pool] = c;

    IMetricOmmPoolFactoryActions(pool)
      .setPoolFees(c.protocolSpreadFeeE6 + c.adminSpreadFeeE6, c.protocolNotionalFeeE8 + c.adminNotionalFeeE8);
    emit PoolAdminSpreadFeeUpdated(pool, newAdminSpreadFeeE6);
    emit PoolAdminNotionalFeeUpdated(pool, newAdminNotionalFeeE8);
  }
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L450-457)
```text
  function setPoolBinAdditionalFees(address pool, int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
  {
    IMetricOmmPoolFactoryActions(pool).setBinAdditionalFees(bin, addFeeBuyE6, addFeeSellE6);
  }
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L487-499)
```text
    uint256 executeAfter = block.timestamp + timelock;
    pendingPriceProvider[pool] = newPriceProvider;
    pendingPriceProviderExecuteAfter[pool] = executeAfter;
    emit PoolPriceProviderChangeProposed(pool, current, newPriceProvider, executeAfter);
  }

  /// @inheritdoc IMetricOmmPoolFactoryPoolAdmin
  function executePoolPriceProviderUpdate(address pool) external override nonReentrant onlyPoolAdmin(pool) {
    address pending = pendingPriceProvider[pool];
    if (pending == address(0)) revert NoPriceProviderChangeProposed();
    uint256 execAfter = pendingPriceProviderExecuteAfter[pool];
    // forge-lint: disable-next-line(block-timestamp) -- timelock enforcement legitimately relies on `block.timestamp`.
    if (block.timestamp < execAfter) revert PriceProviderTimelockNotElapsed(execAfter, block.timestamp);
```

**File:** metric-core/contracts/MetricOmmPool.sol (L437-452)
```text
  function setPoolFees(uint24 newSpreadFeeE6, uint24 newNotionalFeeE8)
    external
    onlyFactory
    nonReentrant(PoolActions.SET_POOL_FEES)
  {
    unchecked {
      if (newSpreadFeeE6 != spreadFeeE6) {
        spreadFeeE6 = newSpreadFeeE6;
        emit SpreadFeeUpdated(newSpreadFeeE6);
      }
      if (newNotionalFeeE8 != notionalFeeE8) {
        notionalFeeE8 = newNotionalFeeE8;
        emit NotionalFeeUpdated(newNotionalFeeE8);
      }
    }
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L464-474)
```text
  function setBinAdditionalFees(int8 bin, uint16 addFeeBuyE6, uint16 addFeeSellE6)
    external
    onlyFactory
    nonReentrant(PoolActions.SET_BIN_ADDITIONAL_FEES)
  {
    if (bin < LOWEST_BIN || bin > HIGHEST_BIN) revert InvalidBinIndex(bin);
    BinState storage s = _binStates[bin];
    s.addFeeBuyE6 = addFeeBuyE6;
    s.addFeeSellE6 = addFeeSellE6;
    emit BinAdditionalFeesUpdated(bin, addFeeBuyE6, addFeeSellE6);
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L540-541)
```text
    uint256 buyFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeBuyE6, ONE_X64, 1e6);
    uint256 sellFeeX64 = baseFeeX64 + Math.mulDiv(binState.addFeeSellE6, ONE_X64, 1e6);
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
