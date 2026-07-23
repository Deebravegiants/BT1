### Title
L2 Price Providers Lack Sequencer Uptime Check, Enabling Stale-Price Swaps After Restart - (`smart-contracts-poc/contracts/PriceProviderL2.sol`, `smart-contracts-poc/contracts/ProtectedPriceProviderL2.sol`)

---

### Summary

`PriceProviderL2` and `ProtectedPriceProviderL2` are explicitly designed for L2 deployment (they carry `FUTURE_TOLERANCE` to handle sequencer clock skew) but neither checks the Chainlink sequencer uptime feed before quoting bid/ask prices. When the L2 sequencer goes offline, oracle prices freeze on-chain. If the last stored oracle price is younger than `MAX_TIME_DELTA` (up to 7 days), the staleness check passes even though the price predates the outage. When the sequencer restarts, an attacker can immediately call `swap()` before any fresh oracle update is pushed, executing against the stale pre-downtime price while the true market price has moved.

---

### Finding Description

Both L2 providers implement a `_isStale` check that compares `refTime` against `block.timestamp`:

```solidity
// PriceProviderL2.sol L135-L150
function _isStale(uint256 refTime, uint256 nowTs, uint256 maxDelta, uint256 futureTol)
    internal pure returns (bool)
{
    if (refTime == 0) return true;
    if (refTime > nowTs) return (refTime - nowTs) > futureTol;
    return (nowTs - refTime) > maxDelta;
}
``` [1](#0-0) 

`MAX_TIME_DELTA` is bounded only at `> 0` and `<= 7 days`: [2](#0-1) 

The full `_getBidAndAskPrice` path performs no sequencer liveness check before accepting the oracle price: [3](#0-2) 

`ProtectedPriceProviderL2` has the identical gap — `_computeBidAsk` checks staleness and price guards but has no sequencer uptime gate: [4](#0-3) 

By contrast, the registry confirms that other contracts in the same system (`ChainlinkVerifierL2`, and the Chainlink-hybrid L2 provider) do carry `sequencerUptimeFeed` and `GRACE_PERIOD`: [5](#0-4) 

The constructor for the Chainlink-hybrid L2 provider explicitly accepts `_sequencerUptimeFeed` and `GRACE_PERIOD`: [6](#0-5) 

`PriceProviderL2` and `ProtectedPriceProviderL2` accept no such parameter and perform no such check.

---

### Impact Explanation

**Bad-price execution leading to direct LP loss.**

Scenario:
1. `MAX_TIME_DELTA` is configured to 1 day (a common reasonable value).
2. The L2 sequencer goes offline. The last oracle price was published 30 minutes before the outage.
3. The market price moves 5–10% during the 4-hour outage.
4. The sequencer restarts. The stored oracle `refTime` is now ~4.5 hours old — well within `MAX_TIME_DELTA`.
5. An attacker calls `swap()` before any oracle keeper pushes a fresh price.
6. `_isStale` returns `false` (4.5 h < 1 day). The pool quotes the pre-outage bid/ask.
7. The attacker buys the underpriced token (or sells the overpriced one) at the stale rate.
8. LPs absorb the loss; the pool's token balances no longer cover fair-value LP claims.

This is a direct loss of LP principal, satisfying the "bad-price execution" and "pool insolvency" impact gates.

---

### Likelihood Explanation

- Both `PriceProviderL2` and `ProtectedPriceProviderL2` are deployed on Arbitrum, Base, Avalanche, BSC, and Berachain (per registry deployments).
- L2 sequencer outages are documented historical events (Arbitrum had a ~7-hour outage in 2022; Base has had brief outages).
- The attack requires no special privilege — any EOA can call `swap()` immediately after sequencer restart.
- The window of vulnerability is bounded by how quickly oracle keepers push a fresh price after restart, which can be minutes.

---

### Recommendation

Add a Chainlink sequencer uptime check with a grace period to both `PriceProviderL2._getBidAndAskPrice()` and `ProtectedPriceProviderL2._getBidAndAskPrice()`, mirroring the pattern already present in `ChainlinkVerifierL2`:

```solidity
// Add immutable:
AggregatorV3Interface public immutable sequencerUptimeFeed;
uint256 public constant GRACE_PERIOD = 3600; // 1 hour

// Add to _getBidAndAskPrice() before the staleness check:
if (address(sequencerUptimeFeed) != address(0)) {
    (, int256 answer, uint256 startedAt,,) = sequencerUptimeFeed.latestRoundData();
    // answer == 0: sequencer is up; answer == 1: sequencer is down
    if (answer != 0 || block.timestamp - startedAt < GRACE_PERIOD) {
        return (0, type(uint128).max); // fail closed
    }
}
```

This ensures that even if the stored oracle price is within `MAX_TIME_DELTA`, swaps are blocked during sequencer downtime and for `GRACE_PERIOD` seconds after restart, giving oracle keepers time to push a fresh price.

---

### Proof of Concept

```
Setup:
  - Deploy PriceProviderL2 on Arbitrum with MAX_TIME_DELTA = 1 days
  - Oracle last updated at T=0 with price = 100 (refTime = T=0)

Attack:
  T=0:    Sequencer goes offline. Oracle price frozen at 100.
  T=4h:   True market price moves to 110 (10% up).
  T=4h:   Sequencer restarts.
  T=4h+ε: Attacker calls pool.swap(zeroForOne=true, ...) before any oracle update.
           PriceProviderL2._isStale(T=0, T=4h, 1 day) → false (4h < 1 day).
           Pool quotes bid/ask around 100 (stale).
           Attacker buys token1 at price 100 when market is 110.
           Attacker immediately sells on a DEX at 110 → 10% profit.
           LPs receive token0 worth 100 but gave up token1 worth 110.

Result: LP loss of ~10% on the swapped amount. Pool balances no longer
        cover fair-value LP claims at current market prices.
```

### Citations

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

**File:** smart-contracts-poc/contracts/PriceProviderL2.sol (L208-248)
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

        // 3. Basic validity — price must be positive, spread must not be stalled marker
        if (mid == 0 || spread >= ORACLE_BPS) {
            return (0, type(uint128).max);
        }

        // 4. Price guard check (moved from oracle)
        (uint128 guardMin, uint128 guardMax) = offchainOracle.priceGuard(offchainFeedId);
        guardMax = guardMax == 0 ? type(uint128).max : guardMax;
        if (mid < guardMin || mid > guardMax) {
            return (0, type(uint128).max);
        }

        // 5. Compute bid/ask from mid + confidence-adjusted spread
        //    confidenceParam multiplies oracle spread; 0 means no spread
        uint256 adjustedSpread = spread * confidenceParam;
        (uint256 bid, uint256 ask) = _getBidAskFrom(mid, adjustedSpread);

        // 6. Apply marginStep adjustment
        (uint256 bidOut, bool bidOk) = _applyBidAdjustments(bid);
        if (!bidOk || bidOut > type(uint128).max) return (0, type(uint128).max);

        (uint256 askOut, bool askOk) = _applyAskAdjustments(ask);
        if (!askOk || askOut > type(uint128).max) return (0, type(uint128).max);

        // 7. Hard invariant: bid must be strictly less than ask.
        //    Can be violated when marginStep < 0 and confidence is too small.
        if (bidOut >= askOut) return (0, type(uint128).max);

        return (uint128(bidOut), uint128(askOut));
    }
```

**File:** smart-contracts-poc/contracts/ProtectedPriceProviderL2.sol (L202-238)
```text
    /// @dev Downstream pricing: staleness, price guard, confidence spread, marginStep.
    function _computeBidAsk(uint256 price, uint256 spread, uint256 refTime)
        internal view returns (uint128, uint128)
    {
        // 1. Staleness check
        if (_isStale(refTime, block.timestamp, MAX_TIME_DELTA, FUTURE_TOLERANCE)) {
            return (0, type(uint128).max);
        }

        // 2. Basic validity — price must be positive, spread must not be stalled marker
        if (price == 0 || spread >= ORACLE_BPS) {
            return (0, type(uint128).max);
        }

        // 3. Price guard check
        (uint128 guardMin, uint128 guardMax) = offchainOracle.priceGuard(offchainFeedId);
        guardMax = guardMax == 0 ? type(uint128).max : guardMax;
        if (price < guardMin || price > guardMax) {
            return (0, type(uint128).max);
        }

        // 4. Compute bid/ask from mid + confidence-adjusted spread
        uint256 adjustedSpread = spread * confidenceParam;
        (uint256 bid, uint256 ask) = _getBidAskFrom(price, adjustedSpread);

        // 5. Apply marginStep adjustment
        (uint256 bidOut, bool bidOk) = _applyBidAdjustments(bid);
        if (!bidOk || bidOut > type(uint128).max) return (0, type(uint128).max);

        (uint256 askOut, bool askOk) = _applyAskAdjustments(ask);
        if (!askOk || askOut > type(uint128).max) return (0, type(uint128).max);

        // 6. Hard invariant: bid must be strictly less than ask.
        if (bidOut >= askOut) return (0, type(uint128).max);

        return (uint128(bidOut), uint128(askOut));
    }
```

**File:** smart-contracts-poc/contract-registry/versions/registry.json (L631-636)
```json
                },
                {
                  "name": "_sequencerUptimeFeed",
                  "type": "address",
                  "internalType": "address"
                },
```

**File:** smart-contracts-poc/contract-registry/versions/registry.json (L5685-5791)
```json
        "ChainlinkVerifierL2": {
          "abi": [
            {
              "type": "constructor",
              "inputs": [
                {
                  "name": "_sequencerUptimeFeed",
                  "type": "address",
                  "internalType": "address"
                }
              ],
              "stateMutability": "nonpayable"
            },
            {
              "type": "function",
              "name": "GRACE_PERIOD",
              "inputs": [],
              "outputs": [
                {
                  "name": "",
                  "type": "uint256",
                  "internalType": "uint256"
                }
              ],
              "stateMutability": "view"
            },
            {
              "type": "function",
              "name": "sequencerUptimeFeed",
              "inputs": [],
              "outputs": [
                {
                  "name": "",
                  "type": "address",
                  "internalType": "contract AggregatorV3Interface"
                }
              ],
              "stateMutability": "view"
            },
            {
              "type": "event",
              "name": "ClOracleRemoved",
              "inputs": [
                {
                  "name": "token",
                  "type": "address",
                  "indexed": true,
                  "internalType": "address"
                }
              ],
              "anonymous": false
            },
            {
              "type": "event",
              "name": "ClOracleSet",
              "inputs": [
                {
                  "name": "token",
                  "type": "address",
                  "indexed": true,
                  "internalType": "address"
                },
                {
                  "name": "oracle",
                  "type": "address",
                  "indexed": true,
                  "internalType": "address"
                },
                {
                  "name": "heartbeat",
                  "type": "uint32",
                  "indexed": false,
                  "internalType": "uint32"
                }
              ],
              "anonymous": false
            },
            {
              "type": "event",
              "name": "ClOracleStateSet",
              "inputs": [
                {
                  "name": "token",
                  "type": "address",
                  "indexed": true,
                  "internalType": "address"
                },
                {
                  "name": "oracle",
                  "type": "address",
                  "indexed": true,
                  "internalType": "address"
                }
              ],
              "anonymous": false
            },
            {
              "type": "error",
              "name": "ClOracleNotFound",
              "inputs": []
            }
          ],
          "methodIdentifiers": {
            "GRACE_PERIOD()": "c1a287e2",
            "sequencerUptimeFeed()": "a7264705"
          }
        }
```
