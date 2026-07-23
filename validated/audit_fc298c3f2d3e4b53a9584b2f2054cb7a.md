### Title
L2 Sequencer Downtime Allows Stale Oracle Prices to Reach Pool Swaps — (`smart-contracts-poc/contracts/PriceProviderL2.sol`)

### Summary
The L2-specific price providers (`PriceProviderL2`, `ProtectedPriceProviderL2`) and the standard `AnchoredPriceProvider` (described as "the one standard provider for public pools") all lack a Chainlink L2 sequencer uptime check. When the L2 sequencer goes offline and resumes, oracle prices from before the outage can pass the existing staleness guard and reach `MetricOmmPool.swap()`, causing bad-price execution and direct LP losses.

### Finding Description

The staleness guard in every price provider is a simple age check against `block.timestamp`:

```solidity
// PriceProviderL2._isStale (L2-aware variant)
function _isStale(uint256 refTime, uint256 nowTs, uint256 maxDelta, uint256 futureTol)
    internal pure returns (bool)
{
    if (refTime == 0) return true;
    if (refTime > nowTs) return (refTime - nowTs) > futureTol;
    return (nowTs - refTime) > maxDelta;   // ← only age, no sequencer check
}
``` [1](#0-0) 

`AnchoredPriceProvider` uses the same pattern (labelled "L1" in its own comment) and is deployed on L2 pools:

```solidity
/// @dev Pure staleness check (L1). Any future refTime is stale.
function _isStale(uint256 refTime, uint256 nowTs, uint256 maxDelta) internal pure returns (bool) {
    if (refTime == 0) return true;
    if (refTime > nowTs) return true;
    return (nowTs - refTime) > maxDelta;
}
``` [2](#0-1) 

Neither contract queries the Chainlink L2 sequencer uptime feed. The attack path is:

1. L2 sequencer goes offline. No oracle keeper transactions can land; `refTime` freezes at the pre-outage value.
2. Real market price moves (e.g., ETH drops from $3 000 to $2 800).
3. Sequencer resumes. `block.timestamp` has advanced, but `refTime` is still the pre-outage timestamp.
4. If `(block.timestamp − refTime) ≤ MAX_TIME_DELTA`, `_isStale` returns `false` — the stale price is accepted.
5. `MetricOmmPool.swap()` calls `_getBidAndAskPriceX64()`, which calls `getBidAndAskPrice()` on the provider:

```solidity
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
``` [3](#0-2) 

6. The stale `(bid, ask)` pair flows into `SwapMath.midAndSpreadFeeX64FromBidAsk` and then `_executeSwap`, which settles real token transfers at the wrong price. [4](#0-3) 

The constructor allows `MAX_TIME_DELTA` up to 7 days, and typical production values (30 s – 5 min) are longer than many historical L2 outages:

```solidity
if (_maxTimeDelta == 0 || _maxTimeDelta > 7 days) revert MaxTimeDeltaOutOfBounds();
MAX_TIME_DELTA = _maxTimeDelta;
``` [5](#0-4) 

`FUTURE_TOLERANCE` only handles clock skew (oracle timestamp slightly ahead of `block.timestamp`); it does not detect or compensate for sequencer downtime. [6](#0-5) 

### Impact Explanation

When the sequencer resumes and the oracle price is stale but within `MAX_TIME_DELTA`:

- **Stale price lower than market** (e.g., asset pumped during outage): traders buy token0 from the pool below market, draining LP value.
- **Stale price higher than market** (e.g., asset dumped during outage): traders sell token0 to the pool above market, again draining LP value.

In both cases `binTotals.scaledToken0` / `scaledToken1` are updated at the wrong exchange rate, permanently mis-accounting LP claims. The loss is proportional to trade size × price deviation and is unbounded by any pool-level cap.

### Likelihood Explanation

The protocol explicitly targets Base, HyperEVM, and other L2s. Base and Arbitrum have each experienced multi-minute sequencer outages. Any outage shorter than `MAX_TIME_DELTA` (which can be minutes) creates the window. No special privilege is required — any address can call `swap()` immediately after the sequencer resumes.

### Recommendation

In `PriceProviderL2`, `ProtectedPriceProviderL2`, and `AnchoredPriceProvider` (when deployed on L2), query the Chainlink L2 sequencer uptime feed before accepting an oracle price. If the sequencer was recently down, revert with `FeedStalled()` for a configurable grace period (e.g., 1 hour) after it recovers:

```solidity
// Example guard to add inside _getBidAndAskPrice():
(, int256 answer, , uint256 updatedAt, ) = sequencerUptimeFeed.latestRoundData();
bool isSequencerUp = (answer == 0);
if (!isSequencerUp) return (0, type(uint128).max);
if (block.timestamp - updatedAt < GRACE_PERIOD) return (0, type(uint128).max);
```

### Proof of Concept

```
Setup:
  Pool on Base, PriceProviderL2, MAX_TIME_DELTA = 120 s
  ETH/USDC pool, oracle mid = 3000e8

T=0:   Oracle pushes refTime=T, mid=3000e8. Pool is live.
T=10:  Base sequencer goes offline. No txs land.
       Real ETH price falls to 2800 (off-chain).
T=90:  Sequencer resumes. refTime is still T=0 (90 s old < 120 s MAX_TIME_DELTA).
       _isStale(T, T+90, 120) → false  ← stale price accepted

T=91:  Attacker calls pool.swap(zeroForOne=false, amountSpecified=+1000e6 USDC)
       _getBidAndAskPriceX64() returns bid/ask anchored at 3000e8 (stale).
       Pool sells ETH at ~3000 USDC/ETH.
       Real market price: 2800 USDC/ETH.
       Attacker receives ETH worth 2800 USDC for 3000 USDC paid → LP loss of 200 USDC per ETH.
       binTotals.scaledToken0 decremented at wrong rate; LP claims permanently under-collateralized.
```

### Citations

**File:** smart-contracts-poc/contracts/PriceProviderL2.sol (L36-38)
```text
    /// @dev L2 sequencer timestamp can lag behind oracle publication time.
    ///      Allows refTime up to FUTURE_TOLERANCE seconds ahead of block.timestamp.
    uint256 public immutable FUTURE_TOLERANCE;
```

**File:** smart-contracts-poc/contracts/PriceProviderL2.sol (L92-95)
```text
        if (_maxTimeDelta == 0 || _maxTimeDelta > 7 days) revert MaxTimeDeltaOutOfBounds();
        if (_futureTolerance > 1 hours) revert FutureToleranceOutOfBounds();
        MAX_TIME_DELTA   = _maxTimeDelta;
        FUTURE_TOLERANCE = _futureTolerance;
```

**File:** smart-contracts-poc/contracts/PriceProviderL2.sol (L135-150)
```text
    function _isStale(
        uint256 refTime,
        uint256 nowTs,
        uint256 maxDelta,
        uint256 futureTol
    ) internal pure returns (bool) {
        if (refTime == 0) return true;

        if (refTime > nowTs) {
            // refTime in the future: tolerate only within futureTol
            return (refTime - nowTs) > futureTol;
        }

        // refTime in the past or equal: check age
        return (nowTs - refTime) > maxDelta;
    }
```

**File:** smart-contracts-poc/contracts/AnchoredPriceProvider.sol (L221-230)
```text
    /// @dev Pure staleness check (L1). Any future refTime is stale.
    function _isStale(
        uint256 refTime,
        uint256 nowTs,
        uint256 maxDelta
    ) internal pure returns (bool) {
        if (refTime == 0) return true;
        if (refTime > nowTs) return true;
        return (nowTs - refTime) > maxDelta;
    }
```

**File:** metric-core/contracts/MetricOmmPool.sol (L242-248)
```text
    (uint256 midPriceX64, uint256 baseFeeX64) =
      SwapMath.midAndSpreadFeeX64FromBidAsk(uint256(bidPriceX64), uint256(askPriceX64));
    SwapMath.InternalSwapParams memory params =
      SwapMath.InternalSwapParams({midPriceX64: midPriceX64, baseFeeX64: baseFeeX64, priceLimitX64: priceLimitX64});

    (int256 amount0Delta, int256 amount1Delta, uint256 protocolFeeAmount) =
      _executeSwap(zeroForOne, amountSpecified, params);
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
