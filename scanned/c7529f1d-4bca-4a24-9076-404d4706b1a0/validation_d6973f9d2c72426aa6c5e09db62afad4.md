### Title
Missing Upper Bound on `priceProviderTimelock` in `createPool` Permanently Locks Pool Into Broken Price Provider - (File: metric-core/contracts/MetricOmmPoolFactory.sol)

### Summary
`MetricOmmPoolFactory.createPool` stores `params.priceProviderTimelock` without any upper-bound validation (other than the special sentinel `type(uint256).max` that marks the provider immutable). A pool creator who fat-fingers this value — e.g., sets it to `type(uint256).max - 1` instead of `type(uint256).max` — produces a pool that is **not** flagged as immutable yet whose timelock is so large that the price-provider update path is permanently bricked. If the underlying oracle later stalls or is deprecated, swaps are permanently broken with no recovery path.

---

### Finding Description

`_validatePoolParameters` validates tokens, admin, fees, and initial amounts, but performs **no check** on `params.priceProviderTimelock`: [1](#0-0) 

The only special handling of `priceProviderTimelock` is the sentinel check for immutability: [2](#0-1) 

Any value other than `type(uint256).max` is stored verbatim: [3](#0-2) 

When the pool admin later calls `proposePoolPriceProvider`, the timelock is added to `block.timestamp`: [4](#0-3) 

Two failure modes arise from an unbounded timelock:

1. **Overflow revert** — if `timelock` is large enough that `block.timestamp + timelock > type(uint256).max`, Solidity 0.8.x reverts on overflow, so `proposePoolPriceProvider` is permanently uncallable.
2. **Unreachable `executeAfter`** — if `timelock` is large but does not overflow (e.g., `type(uint256).max - block.timestamp`), `executeAfter = type(uint256).max`, and `executePoolPriceProviderUpdate` always reverts because `block.timestamp < execAfter` is permanently true: [5](#0-4) 

In both cases the pool is silently stuck with its original price provider. The pool is **not** flagged `immutablePriceProvider` (so neither the factory nor off-chain tooling treats it as immutable), yet the update path is permanently blocked.

When the price provider stalls or is deprecated, `_getBidAndAskPriceX64` reverts with `PriceProviderFailed`, making every swap permanently revert: [6](#0-5) 

The protocol can pause the pool but cannot fix the price provider. LPs can still call `removeLiquidity` (no `whenNotPaused` guard), so principal is recoverable — but the pool's core swap functionality is permanently destroyed.

---

### Impact Explanation

**Medium.** Swaps are permanently broken with no recovery path once the price provider stalls. The pool is in a "false-immutable" state: not flagged immutable, yet the update mechanism is bricked. LPs can withdraw principal via `removeLiquidity`, so direct fund loss is avoided, but the pool's primary function (swap execution) is permanently unusable.

---

### Likelihood Explanation

**Low.** Requires the pool creator to fat-finger `priceProviderTimelock` — e.g., entering `type(uint256).max - 1` instead of `type(uint256).max`, or adding extra digits to a large duration. This is the direct analog of the NFTLootbox `_duration` fat-finger scenario. The risk is compounded because there is no on-chain signal distinguishing a legitimately large timelock from a misconfigured one.

---

### Recommendation

Add an upper-bound check on `priceProviderTimelock` inside `_validatePoolParameters`, excluding the immutable sentinel:

```solidity
uint256 MAX_TIMELOCK = 365 days;
if (
    params.priceProviderTimelock != type(uint256).max &&
    params.priceProviderTimelock > MAX_TIMELOCK
) {
    revert PriceProviderTimelockTooLarge();
}
```

This mirrors the pattern already used for fee caps (`HARD_MAX_SPREAD_FEE_E6`, `HARD_MAX_NOTIONAL_FEE_E8`) and the oracle-layer bound of `MAX_REF_STALENESS <= 7 days` in `AnchoredPriceProvider`: [7](#0-6) 

---

### Proof of Concept

1. Pool creator calls `createPool` with `params.priceProviderTimelock = type(uint256).max - 1`.
2. `_validatePoolParameters` passes — no check on `priceProviderTimelock`.
3. `immutablePriceProvider = (type(uint256).max - 1 == type(uint256).max)` → `false`. Pool is deployed as mutable.
4. `priceProviderTimelock[pool] = type(uint256).max - 1` is stored.
5. LPs add liquidity; the pool operates normally while the price provider is live.
6. Price provider is deprecated / stalls.
7. Every `swap` call hits `_getBidAndAskPriceX64` → `PriceProviderFailed` revert. Swaps are dead.
8. Pool admin calls `proposePoolPriceProvider` with a valid replacement:
   - `uint256 executeAfter = block.timestamp + (type(uint256).max - 1)` → **overflow revert** in Solidity 0.8.x.
9. No recovery path exists. The pool's swap functionality is permanently bricked. [8](#0-7)

### Citations

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L164-164)
```text
    bool immutablePriceProvider = params.priceProviderTimelock == type(uint256).max;
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L213-213)
```text
    priceProviderTimelock[pool] = params.priceProviderTimelock;
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L474-491)
```text
  function proposePoolPriceProvider(address pool, address newPriceProvider)
    external
    override
    nonReentrant
    onlyPoolAdmin(pool)
  {
    PoolImmutables memory p = IMetricOmmPool(pool).getImmutables();
    uint256 timelock = priceProviderTimelock[pool];
    if (p.immutablePriceProvider != address(0)) revert PriceProviderImmutable();
    _validatePriceProvider(p.token0, p.token1, newPriceProvider);

    address mutableProvider = PoolStateLibrary._slot3(pool);
    address current = mutableProvider != address(0) ? mutableProvider : p.immutablePriceProvider;
    uint256 executeAfter = block.timestamp + timelock;
    pendingPriceProvider[pool] = newPriceProvider;
    pendingPriceProviderExecuteAfter[pool] = executeAfter;
    emit PoolPriceProviderChangeProposed(pool, current, newPriceProvider, executeAfter);
  }
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L498-499)
```text
    // forge-lint: disable-next-line(block-timestamp) -- timelock enforcement legitimately relies on `block.timestamp`.
    if (block.timestamp < execAfter) revert PriceProviderTimelockNotElapsed(execAfter, block.timestamp);
```

**File:** metric-core/contracts/MetricOmmPoolFactory.sol (L548-563)
```text
  function _validatePoolParameters(PoolParameters calldata params) internal view {
    if (params.token0 == address(0) || params.token1 == address(0) || params.token0 == params.token1) {
      revert InvalidTokenConfig();
    }
    if (params.admin == address(0)) revert InvalidAdmin();
    _validatePriceProvider(params.token0, params.token1, params.priceProvider);
    if (params.adminFeeDestination == address(0)) revert InvalidAdminFeeDestination();
    if (spreadProtocolFeeE6 > maxProtocolSpreadFeeE6) revert ProtocolFeeTooHigh();
    if (protocolNotionalFeeE8 > maxProtocolNotionalFeeE8) revert ProtocolFeeTooHigh();
    if (params.adminSpreadFeeE6 > maxAdminSpreadFeeE6) revert AdminFeeTooHigh();
    if (params.adminNotionalFeeE8 > maxAdminNotionalFeeE8) revert AdminFeeTooHigh();
    if (params.initialAmount0PerShareE18 == 0 || params.initialAmount1PerShareE18 == 0) {
      revert InvalidInitialAmount();
    }
    if (params.minimalMintableLiquidity == 0) revert InvalidMinimalMintableLiquidity();
  }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L804-813)
```text
  function _getBidAndAskPriceX64() internal returns (uint128 bidPriceX64, uint128 askPriceX64) {
    address activePriceProvider = _resolvedPriceProvider();
    try IPriceProvider(activePriceProvider).getBidAndAskPrice() returns (uint128 bid, uint128 ask) {
      if (bid >= ask) revert BidGreaterThanAsk();
      if (bid == 0) revert BidIsZero();
      return (bid, ask);
    } catch (bytes memory reason) {
      revert PriceProviderFailed(reason);
    }
  }
```

**File:** smart-contracts-poc/contracts/AnchoredPriceProvider.sol (L150-151)
```text
        if (_maxRefStaleness > 7 days) revert MaxRefStalenessOutOfBounds(); // 0 allowed = same-block reference
        MAX_REF_STALENESS = _maxRefStaleness;
```
