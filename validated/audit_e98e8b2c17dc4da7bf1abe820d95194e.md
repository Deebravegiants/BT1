### Title
No Staleness Check on Chainlink Price Feed in `getAssetPrice` - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all validity fields (`roundId`, `updatedAt`, `answeredInRound`), performing zero staleness or validity checks before returning the price. A stale Chainlink price is then used to compute rsETH mint amounts for depositors.

---

### Finding Description

In `contracts/oracles/ChainlinkPriceOracle.sol`, the `getAssetPrice` function fetches the Chainlink price feed but ignores every return value except `price`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

The function does not check:
- `updatedAt == 0` (incomplete round)
- `block.timestamp - updatedAt > stalePriceDelay` (time-based staleness)
- `answeredInRound < roundId` (round-based staleness)
- `price <= 0` (invalid/negative price)

This price is consumed by `LRTOracle.getAssetPrice()`, which delegates directly to this oracle:

```solidity
return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
``` [2](#0-1) 

That result is then used in `LRTDepositPool.getRsETHAmountToMint()` to determine how many rsETH tokens to mint per deposit:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

By contrast, `ChainlinkOracleForRSETHPoolCollateral` in the same repo does perform a partial staleness check (`answeredInRound < roundID`), confirming the team is aware of the pattern but did not apply it to `ChainlinkPriceOracle`. [4](#0-3) 

---

### Impact Explanation

If a Chainlink feed becomes stale (e.g., sequencer downtime, network congestion, feed deprecation), the last reported price — which may be significantly higher or lower than the true market price — is used to compute rsETH mint amounts.

- **Stale price inflated above true value**: A depositor receives more rsETH than their asset is worth, diluting all existing rsETH holders. This constitutes theft of value from existing holders.
- **Stale price deflated below true value**: Depositors receive fewer rsETH tokens than deserved, causing the contract to fail to deliver promised returns.

The first scenario maps to **Critical — direct theft of user funds** (existing rsETH holders' share value is diluted by the over-minted rsETH).

---

### Likelihood Explanation

Chainlink feeds do go stale during L2 sequencer outages, periods of low volatility (heartbeat not triggered), or feed migrations. The entry path requires no special privileges — any user can call `depositAsset()` or `depositETH()` during a stale-price window. The likelihood is **Medium**: stale feed windows are uncommon but historically observed on mainnet and L2s.

---

### Recommendation

Add staleness and validity checks in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (price <= 0) revert InvalidPrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (answeredInRound < roundId) revert StalePrice();
    if (block.timestamp - updatedAt > STALE_PRICE_DELAY) revert StalePrice(); // e.g. 3600s per feed

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

A per-asset `stalePriceDelay` mapping (matching each feed's heartbeat) is preferable to a single global constant.

---

### Proof of Concept

1. Chainlink's `stETH/ETH` feed (or any supported LST feed) goes stale — last reported price is 1.05 ETH per stETH, but true price has dropped to 0.95 ETH.
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 100e18, 0)`.
3. `getRsETHAmountToMint` calls `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale `1.05e18`.
4. rsETH minted = `100e18 * 1.05e18 / rsETHPrice` — ~10.5% more rsETH than the deposit is worth.
5. Attacker immediately redeems rsETH, extracting value from existing holders. [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```
