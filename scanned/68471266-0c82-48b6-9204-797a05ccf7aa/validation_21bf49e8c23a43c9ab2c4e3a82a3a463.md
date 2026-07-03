### Title
No Price Staleness Check in `ChainlinkPriceOracle.getAssetPrice()` Allows Stale Oracle Price to Mint Incorrect rsETH Amounts - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but discards all return values except `price`, performing no staleness validation. This stale price flows directly into rsETH mint calculations for every depositor.

### Finding Description
In `contracts/oracles/ChainlinkPriceOracle.sol`, the `getAssetPrice()` function fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

All five return values of `latestRoundData()` — `roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound` — are available, but only `answer` is used. There is no check that:
- `answeredInRound >= roundId` (detects incomplete/stale rounds)
- `updatedAt != 0` (detects unfinished rounds)
- `updatedAt` is within an acceptable heartbeat window

This price is consumed by `LRTOracle.getAssetPrice()` → `LRTDepositPool.getRsETHAmountToMint()` → `_beforeDeposit()` → `depositAsset()` / `depositETH()`, meaning every deposit minting rsETH relies on this unchecked price.

The codebase itself demonstrates the correct pattern: `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol` performs all three staleness checks before returning a price:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

`ChainlinkPriceOracle` — the oracle used for the core deposit path — has none of these guards.

### Impact Explanation
When a Chainlink feed is stale (e.g., sequencer downtime, network congestion, or a deprecated feed), the last reported price may diverge significantly from the true market price.

- **Stale price inflated (asset crashed, feed not updated):** A depositor submits LST assets at the stale high price, receiving more rsETH than their assets are worth. This dilutes all existing rsETH holders by inflating supply relative to actual backing ETH — a form of share mis-accounting / protocol insolvency.
- **Stale price deflated:** Depositors receive fewer rsETH than deserved — the contract fails to deliver promised returns.

The inflated-price scenario is the critical path: an attacker who observes a stale feed with a price above the true market value can deposit assets and extract value from existing rsETH holders.

### Likelihood Explanation
Chainlink feeds can go stale during L1/L2 network congestion, sequencer outages (on L2 deployments), or when a feed is deprecated. The window of staleness can last minutes to hours. Any depositor can trigger this path permissionlessly via `depositAsset()` or `depositETH()` — no special role is required. The attacker only needs to observe that the feed is stale and that the stale price is favorable.

### Recommendation
Apply staleness checks in `ChainlinkPriceOracle.getAssetPrice()`, consistent with the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    require(answeredInRound >= roundId, "Stale price");
    require(updatedAt != 0, "Round not complete");
    require(price > 0, "Invalid price");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Optionally, add a configurable heartbeat check: `require(block.timestamp - updatedAt <= maxStaleness, "Price too old")`.

### Proof of Concept

**Vulnerable call chain:**

1. Attacker observes Chainlink LST/ETH feed is stale — last reported price is 1.05 ETH per LST, but true market price has dropped to 0.95 ETH per LST.
2. Attacker calls `LRTDepositPool.depositAsset(lstToken, 100e18, minRsETH, "")`.
3. `_beforeDeposit()` calls `getRsETHAmountToMint(lstToken, 100e18)`.
4. `getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(lstToken)`.
5. `LRTOracle.getAssetPrice()` calls `IPriceFetcher(assetPriceOracle[lstToken]).getAssetPrice(lstToken)` — which resolves to `ChainlinkPriceOracle.getAssetPrice()`.
6. `ChainlinkPriceOracle.getAssetPrice()` executes `(, int256 price,,,) = priceFeed.latestRoundData()` — returns stale `1.05e18` with no validation.
7. `rsethAmountToMint = (100e18 * 1.05e18) / rsETHPrice` — attacker receives rsETH valued at 105 ETH worth of backing, having deposited only 95 ETH worth of assets.
8. Existing rsETH holders are diluted by the 10 ETH discrepancy.

**Key file references:** [1](#0-0) 

No staleness check — contrast with the correct implementation: [2](#0-1) 

Deposit mint calculation consuming the unchecked price: [3](#0-2)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
