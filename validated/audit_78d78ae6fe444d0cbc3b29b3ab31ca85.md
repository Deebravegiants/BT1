### Title
`RSETHPriceFeed.latestRoundData()` Returns `updatedAt` Solely from the ETH/USD Feed, Masking a Stale rsETH/ETH Rate - (File: `contracts/oracles/RSETHPriceFeed.sol`)

---

### Summary

`RSETHPriceFeed` is a Chainlink-compatible price feed that computes an rsETH/USD price by multiplying two independent values: the ETH/USD price from a Chainlink aggregator (`ETH_TO_USD`) and the rsETH/ETH exchange rate from `LRTOracle` (`RS_ETH_ORACLE`). However, the `updatedAt` timestamp returned by `latestRoundData()` is taken exclusively from the ETH/USD Chainlink feed. The staleness of the rsETH/ETH component is never reflected in the returned metadata. Any downstream consumer that checks `updatedAt` to validate freshness will only verify the ETH/USD feed's age, not the rsETH/ETH rate's age, allowing a stale rsETH/ETH rate to be silently embedded in an apparently-fresh price.

---

### Finding Description

`RSETHPriceFeed.latestRoundData()` is implemented as:

```solidity
function latestRoundData()
    external
    view
    returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
{
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
```

The `answer` is the product of two independent values:

| Component | Source | Staleness Reflected in `updatedAt`? |
|---|---|---|
| ETH/USD price | `ETH_TO_USD.latestRoundData()` | **Yes** |
| rsETH/ETH rate | `RS_ETH_ORACLE.rsETHPrice()` | **No** |

`RS_ETH_ORACLE.rsETHPrice()` is the value stored in `LRTOracle`, which is updated only when `updateRSETHPrice()` is called. This is a public but permissionless function — it is not called automatically. If it is not called for an extended period (e.g., keeper failure, network congestion, or while the protocol is paused via `LRTOracle.pause()`), the stored `rsETHPrice` becomes stale. Meanwhile, the ETH/USD Chainlink feed continues to update on its own heartbeat.

In that scenario, `latestRoundData()` returns:
- `updatedAt` = the ETH/USD feed's recent timestamp → **appears fresh**
- `answer` = ETH/USD price × stale rsETH/ETH rate → **is stale**

Any consumer that validates `block.timestamp - updatedAt <= maxAge` will pass the check and consume an incorrect price.

The same flaw exists in `getRoundData()`:

```solidity
function getRoundData(uint80 _roundId) external view returns (...) {
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.getRoundData(_roundId);
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
```

---

### Impact Explanation

`RSETHPriceFeed` is deployed on mainnet (per `README.md`: `RSETHPriceFeed (Morph) | 0x4B9C66c2C0d3706AabC6d00D2a6ffD2B68A4E383`) and is consumed by external lending/collateral protocols (e.g., Morpho) to price rsETH as collateral.

**Scenario A — rsETH/ETH rate is stale-low** (rsETH has appreciated but `updateRSETHPrice()` was not called): The feed undervalues rsETH. Morpho positions that are actually healthy are flagged as undercollateralized and liquidated. This constitutes **temporary freezing of user funds** (Medium).

**Scenario B — rsETH/ETH rate is stale-high** (rsETH has depreciated but `updateRSETHPrice()` was not called): The feed overvalues rsETH. Borrowers can draw more debt than their actual collateral supports. This constitutes **direct theft of lender funds** (Critical).

---

### Likelihood Explanation

`LRTOracle.updateRSETHPrice()` is `public whenNotPaused`. It is not called automatically; it depends on off-chain keepers or manual invocation. The ETH/USD Chainlink feed updates on its own heartbeat (typically 1 hour or 0.5% deviation). If the keeper misses even one update cycle while the ETH/USD feed remains active, the combined price silently becomes stale. The protocol's own pause mechanism (`LRTOracle.pause()`, callable by any `PAUSER_ROLE` holder) also blocks `updateRSETHPrice()` while the ETH/USD feed continues updating, directly creating the divergence. Likelihood is **Medium**.

---

### Recommendation

`latestRoundData()` should derive `updatedAt` as the **minimum** of the ETH/USD feed's `updatedAt` and the rsETH oracle's last-update timestamp. `LRTOracle` should expose a `lastUpdated` timestamp (or `RSETHPriceFeed` should track it internally when the rsETH price changes). The corrected logic:

```solidity
function latestRoundData() external view returns (...) {
    (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
    uint256 rsETHLastUpdated = RS_ETH_ORACLE.lastUpdated(); // expose this
    updatedAt = updatedAt < rsETHLastUpdated ? updatedAt : rsETHLastUpdated;
    answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
}
```

This ensures that any consumer's staleness check reflects the freshness of **both** price components, not just the ETH/USD feed.

---

### Proof of Concept

1. `LRTOracle.rsETHPrice()` was last updated 6 hours ago (keeper missed its window).
2. The ETH/USD Chainlink feed updated 5 minutes ago (within its 1-hour heartbeat).
3. A Morpho market calls `RSETHPriceFeed.latestRoundData()`.
4. Returned `updatedAt` = 5 minutes ago → passes any `maxAge = 1 hour` staleness check.
5. Returned `answer` = ETH/USD (fresh) × rsETH/ETH (6 hours stale) → incorrect rsETH/USD price.
6. Morpho uses this price to evaluate collateral health → positions are incorrectly liquidated or over-borrowed against. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/oracles/RSETHPriceFeed.sol (L26-43)
```text
contract RSETHPriceFeed is AggregatorV3Interface {
    /// @notice Price feed for (ETH / USD) pair
    AggregatorV3Interface public immutable ETH_TO_USD;

    /// @notice rsETH oracle contract
    IRSETHOracle public immutable RS_ETH_ORACLE;

    string public description;

    /// @param ethToUSDAggregatorAddress the address of ETH / USD feed
    /// @param rsETHOracle the address of rsETHOracle contract
    /// @param description_ priceFeed description (RSETH / USD)
    constructor(address ethToUSDAggregatorAddress, address rsETHOracle, string memory description_) {
        ETH_TO_USD = AggregatorV3Interface(ethToUSDAggregatorAddress);
        RS_ETH_ORACLE = IRSETHOracle(rsETHOracle);

        description = description_;
    }
```

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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```
