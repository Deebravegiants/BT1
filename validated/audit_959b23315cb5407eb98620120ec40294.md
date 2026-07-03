### Title
`RSETHPriceFeed.latestRoundData()` Returns ETH/USD Feed's `updatedAt` Timestamp While Serving Potentially Stale rsETH Price — (File: `contracts/oracles/RSETHPriceFeed.sol`)

---

### Summary

`RSETHPriceFeed` is a Chainlink-compatible price feed that computes an rsETH/USD price by multiplying the ETH/USD Chainlink answer by the rsETH/ETH rate from `LRTOracle`. However, the `updatedAt` timestamp it returns in `latestRoundData()` is sourced exclusively from the ETH/USD Chainlink feed, not from the rsETH oracle. Because `LRTOracle.rsETHPrice` is a stored value that is only updated when `updateRSETHPrice()` is explicitly called, the rsETH price component can be arbitrarily stale while the returned `updatedAt` reflects a recent ETH/USD heartbeat. Any downstream protocol that performs a standard Chainlink staleness check on `updatedAt` will be deceived into treating a stale rsETH price as fresh.

---

### Finding Description

`RSETHPriceFeed.latestRoundData()` is implemented as follows:

```solidity
// contracts/oracles/RSETHPriceFeed.sol  lines 63-70
function latestRoundData()
    external
    view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
```

All five return values — including `updatedAt` — are taken from `ETH_TO_USD.latestRoundData()`. Only `answer` is then overwritten with the rsETH-adjusted price. The `updatedAt` field therefore reflects the last time the ETH/USD Chainlink feed was updated (typically every ~1 hour via heartbeat), not the last time `LRTOracle.rsETHPrice` was updated.

`LRTOracle.rsETHPrice` is a stored state variable:

```solidity
// contracts/LRTOracle.sol  line 28
uint256 public override rsETHPrice;
```

It is only mutated when `updateRSETHPrice()` or `updateRSETHPriceAsManager()` is called:

```solidity
// contracts/LRTOracle.sol  lines 87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

`updateRSETHPrice()` is permissionless but requires an explicit on-chain call. There is no on-chain enforcement that it is called within any bounded interval. During periods of network congestion, keeper failure, or when `LRTOracle` is paused, `rsETHPrice` can remain stale for an extended and unbounded period.

The `getRoundData()` function has the same flaw:

```solidity
// contracts/oracles/RSETHPriceFeed.sol  lines 53-61
function getRoundData(uint80 _roundId)
    external
    view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.getRoundData(_roundId);
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
```

---

### Impact Explanation

`RSETHPriceFeed` is explicitly designed as a Chainlink `AggregatorV3Interface`-compatible feed for external consumption (e.g., by lending protocols such as Aave, Compound, or any protocol that accepts Chainlink feeds as collateral oracles). These protocols universally perform a staleness check of the form:

```solidity
require(block.timestamp - updatedAt <= MAX_STALENESS, "Stale price");
```

Because `updatedAt` is sourced from the ETH/USD feed (which updates on a ~1-hour heartbeat), this check will pass even when `LRTOracle.rsETHPrice` has not been updated for hours or days. If rsETH has lost value since the last `updateRSETHPrice()` call (e.g., due to a slashing event, EigenLayer strategy loss, or depeg of an underlying LST), the stale (inflated) rsETH price will be accepted as current by the integrating protocol. Users can then borrow against rsETH at an inflated valuation, creating undercollateralized positions. When the price is eventually corrected, the lending protocol suffers bad debt — a direct theft of funds from its depositors.

**Impact**: Critical — direct theft of user funds in any lending protocol integrating `RSETHPriceFeed`.

---

### Likelihood Explanation

`updateRSETHPrice()` is permissionless but not automatically called. The rsETH price update depends on off-chain keepers or manual calls. Realistic staleness scenarios include:

- Keeper downtime or misconfiguration
- `LRTOracle` being paused (which blocks `updateRSETHPrice()` via `whenNotPaused`)
- High gas prices causing keeper delays
- A slashing or depeg event that triggers the price-drop circuit breaker in `_updateRsETHPrice()`, which pauses the oracle and prevents further updates

The ETH/USD Chainlink feed, by contrast, is maintained by Chainlink's decentralized oracle network and updates reliably on its heartbeat. The divergence between the two `updatedAt` sources is therefore a realistic and recurring condition.

**Likelihood**: Medium — keeper failure or oracle pause creates the staleness window; the ETH/USD feed's freshness masks it.

---

### Recommendation

Replace the `updatedAt` field in both `latestRoundData()` and `getRoundData()` with the timestamp at which `LRTOracle.rsETHPrice` was last updated. This requires `LRTOracle` to expose a `rsETHPriceUpdatedAt` timestamp that is written alongside `rsETHPrice` in `_updateRsETHPrice()`. `RSETHPriceFeed` should then return `min(ethToUsdUpdatedAt, rsETHPriceUpdatedAt)` as `updatedAt`, so that the staleness of the composite price reflects the staleness of its least-fresh component.

---

### Proof of Concept

1. `LRTOracle.rsETHPrice` is last updated at `T=0` (e.g., `rsETHPrice = 1.05e18`).
2. Time passes; no one calls `updateRSETHPrice()`. At `T=12h`, a slashing event reduces rsETH's true value to `1.00e18`, but `rsETHPrice` remains `1.05e18`.
3. The ETH/USD Chainlink feed updates normally at `T=12h` (its `updatedAt = T=12h`).
4. A lending protocol calls `RSETHPriceFeed.latestRoundData()`. It receives `updatedAt = T=12h` (from ETH/USD) and `answer` computed using the stale `rsETHPrice = 1.05e18`.
5. The lending protocol's staleness check passes (`block.timestamp - updatedAt = 0`).
6. A user deposits rsETH as collateral. The lending protocol values it at 5% above its true worth.
7. The user borrows the maximum allowed against the inflated collateral value.
8. When `updateRSETHPrice()` is eventually called and the price corrects to `1.00e18`, the user's position is undercollateralized. The lending protocol holds bad debt. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/oracles/RSETHPriceFeed.sol (L53-61)
```text
    function getRoundData(uint80 _roundId)
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
    {
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.getRoundData(_roundId);

        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    }
```

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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```
