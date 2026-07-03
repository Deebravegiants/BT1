### Title
`RSETHPriceFeed.latestRoundData()` Returns ETH/USD Round Metadata Masking rsETH Price Staleness, and `getRoundData()` Returns Incorrect Historical Prices - (File: contracts/oracles/RSETHPriceFeed.sol)

---

### Summary

`RSETHPriceFeed` implements `AggregatorV3Interface` and is deployed as the rsETH/USD price feed for external protocol consumption. Both `latestRoundData()` and `getRoundData()` contain a structural metadata mismatch: round freshness fields (`roundId`, `updatedAt`, `answeredInRound`) are sourced from the underlying ETH/USD Chainlink feed, while `answer` is computed using the current `rsETHPrice` from `LRTOracle`. This means standard Chainlink staleness checks performed by consumers validate ETH/USD freshness, not rsETH oracle freshness. Additionally, `getRoundData(_roundId)` returns an incorrect historical price by multiplying a historical ETH/USD answer by the **current** rsETH/ETH rate.

---

### Finding Description

In `RSETHPriceFeed.latestRoundData()`:

```solidity
function latestRoundData()
    external view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
```

All five return fields except `answer` come from the ETH/USD Chainlink feed. The `updatedAt` timestamp reflects when the ETH/USD feed was last updated, not when `LRTOracle.rsETHPrice` was last written. The `answeredInRound` reflects the ETH/USD round, not any rsETH oracle round concept.

`LRTOracle.rsETHPrice` is updated only when `updateRSETHPrice()` is called. This function is public but not automatically triggered — it depends on off-chain keepers or manual calls. If it has not been called for an extended period, `rsETHPrice` is stale, but `RSETHPriceFeed.latestRoundData()` will still return a recent `updatedAt` from the ETH/USD feed, causing any consumer performing a standard heartbeat check (`block.timestamp - updatedAt < heartbeat`) to incorrectly conclude the rsETH price is fresh.

In `RSETHPriceFeed.getRoundData(_roundId)`:

```solidity
function getRoundData(uint80 _roundId)
    external view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.getRoundData(_roundId);
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
```

This fetches the ETH/USD price at a historical round `_roundId` but multiplies it by the **current** `rsETHPrice`. The returned `answer` is therefore not the rsETH/USD price at that historical round — it is a synthetic value mixing a past ETH/USD price with a present rsETH/ETH rate. Any consumer using historical round data (e.g., for TWAP, dispute resolution, or price verification) receives a structurally incorrect price.

---

### Impact Explanation

External lending protocols, DEXes, or derivatives platforms that integrate `RSETHPriceFeed` as their rsETH/USD oracle face two concrete risks:

1. **Stale rsETH price accepted as fresh**: If `LRTOracle.updateRSETHPrice()` has not been called recently, the rsETH component of the price is stale. Because `updatedAt` reflects ETH/USD freshness, standard heartbeat staleness checks pass. Protocols may accept an outdated rsETH valuation, enabling users to borrow against overvalued rsETH collateral or avoid liquidation when they should be liquidated.

2. **Incorrect historical prices from `getRoundData`**: Any protocol querying historical round data receives a price that is not the actual rsETH/USD price at that round. This corrupts any TWAP or historical price verification logic built on top of this feed.

The impact maps to **Medium — Temporary freezing of funds** (if protocols freeze rsETH positions on incorrect price data) or **Low — Contract fails to deliver promised returns** (incorrect pricing without direct fund loss in the LRT-rsETH protocol itself).

---

### Likelihood Explanation

`updateRSETHPrice()` is a public function with no access restriction, so any actor can call it. However, there is no on-chain enforcement that it is called within any time window. During periods of low activity, keeper failure, or network congestion, `rsETHPrice` can become stale while the ETH/USD feed continues updating normally. The metadata mismatch in `getRoundData` is unconditional — it is always incorrect for any historical round, regardless of oracle freshness.

Likelihood is **Medium**: the `latestRoundData` staleness masking requires a keeper gap, while the `getRoundData` historical price corruption is always present.

---

### Recommendation

1. **`latestRoundData()`**: Track the timestamp of the last `rsETHPrice` update in `LRTOracle` (e.g., `rsETHPriceUpdatedAt`). Return `min(ethToUsdUpdatedAt, rsETHPriceUpdatedAt)` as `updatedAt` so that consumers' staleness checks reflect the freshness of the least-recently-updated component.

2. **`getRoundData()`**: Either revert with `NotSupported()` (since accurate historical rsETH/USD prices cannot be reconstructed without a historical rsETH price index), or document clearly that historical round data is not meaningful for this feed and remove the function from the interface.

3. Consider storing a monotonically increasing `rsETHRoundId` in `LRTOracle` that increments on each `updateRSETHPrice()` call, and returning it as `answeredInRound` in `latestRoundData()`.

---

### Proof of Concept

**Scenario — Stale rsETH price masked as fresh:**

1. At `T=0`, `LRTOracle.updateRSETHPrice()` is called. `rsETHPrice = 1.05e18`. ETH/USD feed `updatedAt = T`.
2. At `T+25h`, ETH/USD feed updates normally. ETH/USD `updatedAt = T+25h`. `rsETHPrice` has not been updated (keeper offline).
3. A lending protocol calls `RSETHPriceFeed.latestRoundData()`.
4. Returned: `updatedAt = T+25h` (from ETH/USD), `answer = 1.05e18 * currentEthUsdPrice / 1e18` (stale rsETH rate).
5. Protocol checks `block.timestamp - updatedAt = 0 < heartbeat` → staleness check passes.
6. Protocol prices rsETH using a 25-hour-old rsETH/ETH rate. If rsETH/ETH has declined (e.g., slashing event), rsETH is overvalued.
7. Attacker deposits rsETH as collateral at the inflated price and borrows the maximum allowed, then defaults.

**Scenario — Incorrect historical price from `getRoundData`:**

1. At round `R` (6 months ago), ETH/USD = 2000 USD, rsETH/ETH = 1.02. True rsETH/USD at round R = 2040 USD.
2. Today, rsETH/ETH = 1.08. ETH/USD = 3000 USD.
3. Protocol calls `RSETHPriceFeed.getRoundData(R)`.
4. Returned: `answer = 1.08e18 * 2000e8 / 1e18 = 2160e8` (2160 USD) — not the actual 2040 USD at round R.
5. Any TWAP or historical verification using this value is corrupted. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/oracles/RSETHPriceFeed.sol (L53-70)
```text
    function getRoundData(uint80 _roundId)
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
    {
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.getRoundData(_roundId);

        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    }

    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
    {
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    }
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
