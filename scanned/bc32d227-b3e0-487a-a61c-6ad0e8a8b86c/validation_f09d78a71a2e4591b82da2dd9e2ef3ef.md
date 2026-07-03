### Title
Stale `rsETHPrice` Masked by ETH/USD Timestamp in `RSETHPriceFeed.latestRoundData()` - (File: contracts/oracles/RSETHPriceFeed.sol)

---

### Summary

`RSETHPriceFeed` computes `rsETH/USD` as the product of two independent data sources — a live Chainlink ETH/USD feed and the stored `rsETHPrice` from `LRTOracle` — but returns only the Chainlink feed's `updatedAt` timestamp. The staleness of the `rsETHPrice` component is completely invisible to any integrating protocol that relies on `updatedAt` for freshness checks.

---

### Finding Description

`RSETHPriceFeed` implements `AggregatorV3Interface` and is intended to be consumed by external protocols (lending markets, AMMs, etc.) as a standard Chainlink-compatible `rsETH/USD` price feed.

In `latestRoundData()`:

```solidity
// contracts/oracles/RSETHPriceFeed.sol lines 63-70
function latestRoundData()
    external view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
```

The returned `answer` is the product of two feeds:
1. **ETH/USD** — from Chainlink's `ETH_TO_USD` aggregator, continuously updated on-chain.
2. **rsETH/ETH** — from `RS_ETH_ORACLE.rsETHPrice()`, which reads the `rsETHPrice` state variable stored in `LRTOracle`.

The `rsETHPrice` in `LRTOracle` is a stored state variable that is only updated when `updateRSETHPrice()` is explicitly called:

```solidity
// contracts/LRTOracle.sol line 28
uint256 public override rsETHPrice;

// contracts/LRTOracle.sol line 87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

This is a push-based oracle — there is no on-chain guarantee of freshness. If `updateRSETHPrice()` is not called for an extended period (e.g., keeper failure, protocol pause, or network congestion), `rsETHPrice` becomes stale. However, `latestRoundData()` will still return the ETH/USD Chainlink feed's `updatedAt`, which may be very recent, making the combined price appear fresh to any integrator checking `updatedAt`.

The same masking occurs in `getRoundData()`:

```solidity
// contracts/oracles/RSETHPriceFeed.sol lines 53-61
function getRoundData(uint80 _roundId)
    external view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.getRoundData(_roundId);
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
```

---

### Impact Explanation

Any external protocol integrating `RSETHPriceFeed` as a Chainlink-compatible oracle and applying a staleness check on `updatedAt` will only be validating the ETH/USD feed's freshness. The `rsETH/ETH` component's age is entirely invisible. If `rsETHPrice` is stale (e.g., reflecting a higher pre-slashing or pre-depeg value), the combined `rsETH/USD` price returned will be inflated relative to reality, while `updatedAt` still passes any freshness guard. This causes the contract to fail to deliver its promised function — an accurate, fresh `rsETH/USD` price — without the integrator being able to detect it.

**Impact: Low — Contract fails to deliver promised returns, but doesn't directly lose value within LRT-rsETH itself.**

---

### Likelihood Explanation

`updateRSETHPrice()` is a public function that must be called externally to refresh `rsETHPrice`. Any scenario where this call is delayed — keeper downtime, protocol pause (which blocks `updateRSETHPrice()` via `whenNotPaused`), or simply low call frequency — results in a stale `rsETHPrice` being silently propagated through `RSETHPriceFeed`. The `whenNotPaused` modifier on `updateRSETHPrice()` is particularly notable: if the protocol is paused, `rsETHPrice` cannot be updated at all, yet `RSETHPriceFeed.latestRoundData()` continues to serve the stale value with a fresh-looking `updatedAt`.

---

### Recommendation

`latestRoundData()` should return the minimum of the ETH/USD feed's `updatedAt` and the timestamp at which `rsETHPrice` was last updated. This requires `LRTOracle` to store and expose a `rsETHPriceUpdatedAt` timestamp alongside `rsETHPrice`, and `RSETHPriceFeed` to use `MIN(ethUsdUpdatedAt, rsETHPriceUpdatedAt)` as the returned `updatedAt`. This ensures any integrator's staleness check covers both components of the derived price.

---

### Proof of Concept

1. `LRTOracle.updateRSETHPrice()` is last called at time `T`. `rsETHPrice` is stored as `P_rsETH`.
2. Time passes; ETH/USD Chainlink feed continues to update normally. At time `T + 2 hours`, `ETH_TO_USD.latestRoundData()` returns `updatedAt = T + 2 hours`.
3. A lending protocol calls `RSETHPriceFeed.latestRoundData()`. It receives `updatedAt = T + 2 hours` (from ETH/USD) and `answer = P_rsETH * ETH_USD_price / 1e18`.
4. The lending protocol's staleness check passes (e.g., `require(block.timestamp - updatedAt < 3600)`), because `updatedAt` is only 0 seconds old from the protocol's perspective.
5. The lending protocol accepts the stale `rsETH/USD` price as valid, potentially allowing borrowing against an outdated rsETH valuation.

The root cause is at: [1](#0-0) 

The stale component is: [2](#0-1) 

Updated only via: [3](#0-2)

### Citations

**File:** contracts/oracles/RSETHPriceFeed.sol (L63-70)
```text
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
    {
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    }
```

**File:** contracts/LRTOracle.sol (L28-28)
```text
    uint256 public override rsETHPrice;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```
