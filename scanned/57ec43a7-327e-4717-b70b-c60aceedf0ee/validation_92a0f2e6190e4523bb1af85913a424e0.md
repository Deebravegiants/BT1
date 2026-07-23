### Title
L2 Price Providers Accept Stale Prices After Sequencer Restart Without Sequencer Uptime Check — (`smart-contracts-poc/contracts/PriceProviderL2.sol`, `smart-contracts-poc/contracts/ProtectedPriceProviderL2.sol`)

---

### Summary

`PriceProviderL2` and `ProtectedPriceProviderL2` are explicitly deployed on L2 chains (Arbitrum). Both rely solely on a timestamp-delta staleness check (`_isStale`) to validate oracle prices. Neither contract checks whether the L2 sequencer is currently live. When the Arbitrum sequencer goes down, no new price reports can be pushed to the on-chain oracle (`ChainlinkOracle` / `PythOracle`). When the sequencer restarts, the stored price retains its pre-outage `refTime`. If the outage duration is shorter than `MAX_TIME_DELTA`, the old price passes the staleness check and is served to the pool as fresh — even though the real market price may have moved substantially during the outage.

---

### Finding Description

`PriceProviderL2._getBidAndAskPrice()` reads the oracle price and applies a staleness check:

```solidity
(uint256 mid, uint256 spread, , uint256 refTime) =
    IPricedOracle(address(offchainOracle)).price(offchainFeedId, msg.sender);

if (_isStale(refTime, block.timestamp, MAX_TIME_DELTA, FUTURE_TOLERANCE)) {
    return (0, type(uint128).max);
}
```

`_isStale` only checks whether `(nowTs - refTime) > MAX_TIME_DELTA`:

```solidity
function _isStale(uint256 refTime, uint256 nowTs, uint256 maxDelta, uint256 futureTol)
    internal pure returns (bool)
{
    if (refTime == 0) return true;
    if (refTime > nowTs) return (refTime - nowTs) > futureTol;
    return (nowTs - refTime) > maxDelta;
}
```

The oracle backends (`ChainlinkOracle`, `PythOracle`) are push-based: prices are stored only when someone calls `updateReport()` / the Pyth fallback. When the Arbitrum sequencer is down, no transactions can land on L2, so no fresh price can be pushed. The stored `refTime` is frozen at the last pre-outage push. When the sequencer restarts:

- `refTime` = time of last push before outage (e.g., `T`)
- `block.timestamp` = `T + outage_duration`
- If `outage_duration < MAX_TIME_DELTA`, `_isStale` returns `false`
- The pool receives the pre-outage price as if it were current

`MAX_TIME_DELTA` is configurable up to 7 days, but even a conservative 30-minute setting creates a 30-minute exploitation window after every sequencer restart. There is no sequencer uptime feed check anywhere in either L2 provider contract.

The `FUTURE_TOLERANCE` field addresses only clock skew (sequencer timestamp lagging oracle publication time), not sequencer downtime.

---

### Impact Explanation

A malicious actor monitoring the sequencer can, immediately after restart and before any fresh price is pushed:

1. Execute a swap through `MetricOmmPool` → `getBidAndAskPrice()` → `PriceProviderL2._getBidAndAskPrice()`.
2. The pool prices the swap using the pre-outage bid/ask.
3. If the real market price moved during the outage (e.g., a 5–10% move is common during volatile periods that often coincide with sequencer stress), the attacker receives tokens at a stale favorable price.
4. LPs bear the loss: the pool's token balances no longer cover LP claims at fair value.

This is a direct loss of LP principal — a bad-price execution reaching a pool swap — satisfying the allowed impact gate.

---

### Likelihood Explanation

Arbitrum sequencer outages have occurred historically (multiple incidents documented). The vulnerability requires no special permissions: any address can call `swap()` on the pool. The exploitation window opens automatically on every sequencer restart and closes only when a fresh price is pushed. Given that price pushers are off-chain bots that may themselves be delayed after a restart, the window can be minutes to tens of minutes — sufficient for a prepared attacker.

---

### Recommendation

Add a Chainlink L2 sequencer uptime check in both `PriceProviderL2` and `ProtectedPriceProviderL2`. The sequencer feed address should be an immutable set at construction. In `_getBidAndAskPrice()` (or `_computeBidAsk()`), before using the price, verify:

```solidity
// Chainlink sequencer uptime feed (e.g., Arbitrum: 0xFdB631F5EE196F0ed6FAa767959853A9F217697D)
(, int256 answer, uint256 startedAt, ,) = sequencerUptimeFeed.latestRoundData();
// answer == 0 means sequencer is up; 1 means down
require(answer == 0, SequencerDown());
// Optionally enforce a grace period after restart
require(block.timestamp - startedAt > GRACE_PERIOD, SequencerJustRestarted());
```

This mirrors the fix applied in the Bond Protocol reference (PR #53) and is the standard Chainlink recommendation for L2 deployments.

---

### Proof of Concept

1. Assume `MAX_TIME_DELTA = 30 minutes`, last price push at `T = block.timestamp - 5 minutes`.
2. Arbitrum sequencer goes down at `T + 1 minute`; real ETH price drops 8% during outage.
3. Sequencer restarts at `T + 20 minutes`; stored `refTime = T + 1 minute` (last push before outage).
4. Attacker calls `MetricOmmPool.swap(...)` before any fresh price is pushed.
5. `PriceProviderL2._getBidAndAskPrice()` reads `refTime = T + 1 minute`; `nowTs - refTime = 19 minutes < 30 minutes` → `_isStale` returns `false`.
6. Pool executes swap at pre-outage (8% inflated) ask price; attacker receives excess tokens; LPs are underpaid. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** smart-contracts-poc/contracts/PriceProviderL2.sol (L208-217)
```text
    function _getBidAndAskPrice() internal returns (uint128, uint128) {
        // 1. Read via the unified price(feedId, pool) path, forwarding the pool (msg.sender).
        //    refTime is already in seconds.
        (uint256 mid, uint256 spread, , uint256 refTime) =
            IPricedOracle(address(offchainOracle)).price(offchainFeedId, msg.sender);

        // 2. Staleness check
        if (_isStale(refTime, block.timestamp, MAX_TIME_DELTA, FUTURE_TOLERANCE)) {
            return (0, type(uint128).max);
        }
```

**File:** smart-contracts-poc/contracts/ProtectedPriceProviderL2.sol (L138-153)
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

**File:** smart-contracts-poc/contracts/ProtectedPriceProviderL2.sol (L196-209)
```text
    function _getBidAndAskPrice() internal returns (uint128, uint128) {
        (uint256 mid, uint256 spread, , uint256 refTime) =
            IPricedOracle(address(offchainOracle)).price(offchainFeedId, msg.sender);
        return _computeBidAsk(mid, spread, refTime);
    }

    /// @dev Downstream pricing: staleness, price guard, confidence spread, marginStep.
    function _computeBidAsk(uint256 price, uint256 spread, uint256 refTime)
        internal view returns (uint128, uint128)
    {
        // 1. Staleness check
        if (_isStale(refTime, block.timestamp, MAX_TIME_DELTA, FUTURE_TOLERANCE)) {
            return (0, type(uint128).max);
        }
```
