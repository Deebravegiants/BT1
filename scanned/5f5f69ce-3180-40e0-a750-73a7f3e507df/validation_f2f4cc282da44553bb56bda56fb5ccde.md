### Title
Missing Staleness and Validity Checks on Chainlink `latestRoundData()` Return Values - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards `roundId`, `updatedAt`, and `answeredInRound`, performing no staleness, completeness, or sign checks on the returned price. A stale or zero Chainlink price propagates directly into rsETH mint calculations, enabling incorrect rsETH issuance to depositors.

---

### Finding Description

In `ChainlinkPriceOracle.getAssetPrice()`, the call to `latestRoundData()` uses a wildcard destructure that ignores every return value except `price`: [1](#0-0) 

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

None of the following safety checks are present:
- `price > 0` — a zero or negative price is silently cast to a huge `uint256` (via underflow) or zero, corrupting the rate.
- `updatedAt != 0` — a zero timestamp signals an incomplete round.
- `answeredInRound >= roundId` — a stale round is accepted as current.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same repository correctly validates all three conditions: [2](#0-1) 

The same omission exists in `RSETHPriceFeed.latestRoundData()`, which forwards the raw ETH/USD Chainlink answer without any validation before multiplying it by the rsETH/ETH rate: [3](#0-2) 

---

### Impact Explanation

`ChainlinkPriceOracle.getAssetPrice()` is the price source for LST collateral assets (stETH, cbETH, rETH, etc.) deposited into the protocol. The returned price feeds into `LRTOracle`, which computes the rsETH/ETH exchange rate used by `LRTDepositPool` to determine how many rsETH tokens to mint per deposit.

If Chainlink returns a stale price (e.g., during a sequencer outage, network congestion, or a Chainlink heartbeat gap):
- A stale **inflated** price causes the protocol to mint **more rsETH** than the deposited asset is worth — direct theft of value from existing rsETH holders (dilution of backing).
- A stale **deflated** or zero price causes the protocol to mint **fewer rsETH** or revert with an arithmetic error, temporarily freezing deposits.

**Impact: Medium — Temporary freezing of funds / incorrect rsETH issuance (share mis-accounting).**

---

### Likelihood Explanation

Chainlink feeds can lag during periods of low volatility (heartbeat-only updates, e.g., 24 h for some feeds) or during L2 sequencer downtime. No external attacker action is required — the condition arises from normal Chainlink operational behavior. Any unprivileged depositor calling `LRTDepositPool.depositAsset()` during such a window triggers the vulnerable path.

**Likelihood: Medium.**

---

### Recommendation

Apply the same pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    require(price > 0, "Chainlink price <= 0");
    require(updatedAt != 0, "Incomplete round");
    require(answeredInRound >= roundId, "Stale price");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Apply equivalent checks inside `RSETHPriceFeed.latestRoundData()` before using the ETH/USD answer.

---

### Proof of Concept

1. Chainlink's ETH/stETH feed enters a heartbeat-only update window; `updatedAt` is 23 hours old and `answeredInRound < roundId`.
2. An attacker (or any user) calls `LRTDepositPool.depositAsset(stETH, amount)`.
3. `LRTDepositPool` calls `LRTOracle` → `ChainlinkPriceOracle.getAssetPrice(stETH)`.
4. `getAssetPrice` calls `latestRoundData()`, receives the stale price, and returns it without any revert.
5. `LRTOracle` computes an incorrect rsETH/ETH rate using the stale collateral price.
6. `LRTDepositPool` mints rsETH to the depositor at the wrong rate — either over-minting (diluting existing holders) or under-minting (loss to depositor).

The root cause is exclusively in `ChainlinkPriceOracle.getAssetPrice()` at: [4](#0-3)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L27-33)
```text
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

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
