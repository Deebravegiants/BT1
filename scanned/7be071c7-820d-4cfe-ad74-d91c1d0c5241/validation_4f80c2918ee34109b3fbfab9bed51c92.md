### Title
No Chainlink Price Feed Staleness Check Allows Stale Prices to Drive rsETH Minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all staleness-related return values (`updatedAt`, `roundId`, `answeredInRound`). There is no heartbeat or time-based staleness check of any kind. A stale price is silently accepted and used to compute how many rsETH tokens to mint for a depositor, enabling share/asset mis-accounting that can result in over-minting of rsETH and protocol insolvency.

### Finding Description
In `contracts/oracles/ChainlinkPriceOracle.sol`, `getAssetPrice()` fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. Only `answer` is used; `updatedAt` (the timestamp of the last oracle update) and `answeredInRound` are silently discarded. No comparison of `updatedAt` against `block.timestamp` with any heartbeat threshold is performed, and no `answeredInRound < roundId` check is made.

This oracle is registered as the price source for LST assets (e.g., stETH, cbETH) via `LRTOracle.assetPriceOracle`. It is called in two critical paths:

1. **`LRTDepositPool.getRsETHAmountToMint()`** — determines how many rsETH tokens a depositor receives:
   ```solidity
   rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
   ``` [2](#0-1) 

2. **`LRTOracle._updateRsETHPrice()`** — computes total ETH in protocol to set the global rsETH price, which feeds into all subsequent minting calculations. [3](#0-2) 

`ChainlinkOracleForRSETHPoolCollateral` (used in the pool path) also lacks a time-based staleness check — it only checks `answeredInRound < roundID`, a deprecated Chainlink pattern that does not catch time-based staleness:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
``` [4](#0-3) 

### Impact Explanation
If a Chainlink feed becomes stale (e.g., the LST/ETH feed stops updating due to network congestion or oracle downtime), the last reported price — which may be significantly higher than the true current price — is used without any revert or warning. A depositor calling `depositAsset()` during this window receives rsETH minted at the inflated stale price, extracting more value than they deposited. This dilutes all existing rsETH holders and can push the protocol toward insolvency. Impact: **Critical — direct theft of funds / protocol insolvency**.

### Likelihood Explanation
Chainlink feeds do go stale during network congestion events, sequencer outages (on L2s), or oracle node failures. The protocol is deployed on multiple chains (Ethereum, Arbitrum, Optimism, etc.) where such events have historically occurred. No external trigger or privileged access is required — any depositor benefits automatically when the feed is stale. Likelihood: **Medium-High**.

### Recommendation
Add a per-feed configurable heartbeat parameter and validate `updatedAt` against it in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
mapping(address asset => uint256 heartbeat) public assetHeartbeat;

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    require(answeredInRound >= roundId, "Stale price");
    require(block.timestamp - updatedAt <= assetHeartbeat[asset], "Price too old");
    require(price > 0, "Invalid price");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Apply the same fix to `ChainlinkOracleForRSETHPoolCollateral.getRate()`.

### Proof of Concept
1. The stETH/ETH Chainlink feed on Ethereum has a 24-hour heartbeat. During a period of low volatility, the feed may not update for up to 24 hours.
2. Suppose the true stETH/ETH price drops from 1.0 ETH to 0.95 ETH due to a depeg event, but the Chainlink feed has not yet updated (still reporting 1.0 ETH).
3. An attacker calls `LRTDepositPool.depositAsset(stETH, 100e18, 0, "")`.
4. `getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale price of `1.0e18` instead of `0.95e18`.
5. The attacker receives rsETH minted at the inflated rate: `100e18 * 1.0e18 / rsETHPrice` instead of `100e18 * 0.95e18 / rsETHPrice` — approximately 5.26% more rsETH than deserved.
6. The attacker immediately redeems or sells the excess rsETH, extracting value from existing holders. No admin action or special role is required. [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L231-234)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-31)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
```
