### Title
No Time-Based Staleness Check on Any Chainlink Feed Allows Stale Price Consumption - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle` calls `latestRoundData()` for every supported LST asset but completely discards the `updatedAt` return value, applying **no** time-based freshness check to any feed. Because the contract serves multiple assets (stETH, cbETH, rETH, etc.) each with different Chainlink heartbeats, a feed that has gone stale will silently supply an outdated price that is used directly to compute rsETH mint amounts and withdrawal amounts.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` fetches the price as follows:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol  L49-L55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();   // updatedAt silently dropped
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

The five-tuple returned by `latestRoundData()` is `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The destructuring `(, int256 price,,,)` silently discards `updatedAt`, so there is no check of the form `require(block.timestamp - updatedAt <= heartbeat)`. This is the direct analog of the reported vulnerability: the original contract used a single shared heartbeat for feeds with different update frequencies; here the heartbeat check is absent entirely for every feed.

`LRTOracle._getTotalEthInProtocol()` iterates over all supported assets and calls `getAssetPrice()` for each one to compute total protocol TVL:

```solidity
// contracts/LRTOracle.sol  L336-L343
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);          // stale price accepted silently
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    ...
}
``` [2](#0-1) 

`LRTDepositPool.getRsETHAmountToMint()` uses the same oracle path to determine how many rsETH tokens to mint per deposit:

```solidity
// contracts/LRTDepositPool.sol  L519-L521
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

`LRTWithdrawalManager.getExpectedAssetAmount()` uses the same oracle path to determine how many underlying tokens a withdrawer receives:

```solidity
// contracts/LRTWithdrawalManager.sol  L593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [4](#0-3) 

### Impact Explanation
If a Chainlink feed for any supported LST goes stale at a price **above** the current market price (e.g., during network congestion or a Chainlink node outage), a depositor can supply that LST and receive more rsETH than the asset is currently worth, diluting all existing rsETH holders. Conversely, a stale price **below** market causes withdrawers to receive more underlying tokens than they should, directly draining protocol reserves. Both directions constitute theft of yield or funds from other protocol participants. Impact: **High — theft of unclaimed yield / protocol insolvency in extreme staleness scenarios**.

### Likelihood Explanation
Chainlink feeds for LSTs (e.g., stETH/ETH, cbETH/ETH) have heartbeats ranging from 1 hour to 24 hours. Network congestion events, Chainlink node outages, or L2 sequencer issues can cause feeds to miss their heartbeat. This is a well-documented, historically observed condition. Any unprivileged depositor or withdrawer can exploit the window between the feed going stale and an admin noticing. Likelihood: **Medium**.

### Recommendation
Add a per-asset configurable `maxStaleness` mapping in `ChainlinkPriceOracle` and enforce it in `getAssetPrice()`:

```solidity
mapping(address asset => uint256 maxStaleness) public assetMaxStaleness;

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
    require(block.timestamp - updatedAt <= assetMaxStaleness[asset], "Stale price");
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Each asset's `maxStaleness` should be set to slightly above its feed's documented heartbeat (e.g., 3600 + buffer for ETH/ETH feeds, 86400 + buffer for stablecoin feeds).

### Proof of Concept
1. Assume stETH/ETH Chainlink feed (heartbeat: 1 hour) has not been updated for 3 hours due to network congestion. Its last reported price was `1.001 ETH` but the current market price is `0.998 ETH`.
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18)`.
3. `getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale `1.001e18` with no revert.
4. rsETH minted = `1000e18 * 1.001e18 / rsETHPrice` — attacker receives ~0.3% more rsETH than the current fair value of their deposit.
5. Attacker immediately redeems rsETH via `LRTWithdrawalManager`, extracting value from honest rsETH holders. [1](#0-0) [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L336-343)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
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

**File:** contracts/LRTWithdrawalManager.sol (L593-593)
```text
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
