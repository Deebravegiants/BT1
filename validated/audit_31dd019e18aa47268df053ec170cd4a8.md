### Title
No Chainlink Price Feed Staleness Check in `ChainlinkPriceOracle.getAssetPrice()` Allows Stale Prices to Inflate rsETH Minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but completely discards the `updatedAt` timestamp, performing zero time-based staleness validation. A stale (inflated) asset price flows directly into rsETH minting, allowing a depositor to receive more rsETH than their deposit is worth, diluting existing holders.

### Finding Description
In `contracts/oracles/ChainlinkPriceOracle.sol`, the `getAssetPrice()` function fetches the Chainlink price but silently drops all return values except `price`:

```solidity
// Line 52 — updatedAt is never captured or checked
(, int256 price,,,) = priceFeed.latestRoundData();
```

There is no `block.timestamp - updatedAt < threshold` guard of any kind. This is the direct analog of M-6, but worse: the original vulnerability had an incorrect (too-loose) threshold; here there is **no threshold at all**.

The stale price then propagates through the following call chain:

1. `ChainlinkPriceOracle.getAssetPrice(asset)` — returns stale price
2. `LRTOracle.getAssetPrice(asset)` (line 157) — delegates to the oracle above
3. `LRTOracle._getTotalEthInProtocol()` (line 339) — multiplies stale price by total asset deposits
4. `LRTOracle._updateRsETHPrice()` (line 250) — computes `newRsETHPrice` from inflated TVL
5. `LRTDepositPool.getRsETHAmountToMint()` (line 520) — uses `lrtOracle.getAssetPrice(asset) / lrtOracle.rsETHPrice()` to determine how many rsETH tokens to mint per deposit

If a supported LST's Chainlink feed goes stale at an inflated price, every subsequent deposit of that asset mints excess rsETH, directly diluting the ETH-per-rsETH ratio for all existing holders. [1](#0-0) [2](#0-1) [3](#0-2) 

### Impact Explanation
**High — Theft of unclaimed yield / share mis-accounting.**

When a Chainlink feed for any supported LST (e.g., stETH/ETH, cbETH/ETH) goes stale at a price above the true market rate, every depositor who calls `depositAsset()` during the stale window receives more rsETH than their deposit is worth. The excess rsETH represents a claim on ETH that was already owned by existing holders, constituting a direct transfer of value from existing rsETH holders to the new depositor. [4](#0-3) [5](#0-4) 

### Likelihood Explanation
**Medium.** Chainlink feeds can go stale during network congestion, sequencer downtime (on L2), or when a feed is deprecated. The protocol supports multiple LST assets, each with its own feed and heartbeat. The absence of any staleness check means the window of exploitability equals the full duration of any feed outage. A sophisticated depositor monitoring on-chain feed timestamps can identify and exploit the stale window permissionlessly. [1](#0-0) 

### Recommendation
Capture `updatedAt` from `latestRoundData()` and assert it is within an acceptable heartbeat per asset. Since different Chainlink feeds have different heartbeats (e.g., stETH/ETH is 86400 s, cbETH/ETH is 86400 s, but others may be 3600 s), store a per-asset `maxStaleness` mapping in `ChainlinkPriceOracle` and validate accordingly — exactly the fix recommended in M-6:

```solidity
mapping(address asset => uint256 maxStaleness) public assetMaxStaleness;

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
    require(block.timestamp - updatedAt <= assetMaxStaleness[asset], "stale price");
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

### Proof of Concept
1. Assume stETH/ETH Chainlink feed last updated at `T=0` with price `1.05e18` (stETH trading at a premium).
2. At `T=7200` the feed goes stale (true price has dropped to `1.00e18`), but `latestRoundData()` still returns `1.05e18` and `updatedAt = T=0`.
3. An attacker calls `LRTDepositPool.depositAsset(stETH, 100e18)`.
4. `getRsETHAmountToMint` computes: `(100e18 * 1.05e18) / rsETHPrice` — 5% more rsETH than the deposit is worth.
5. The attacker immediately requests withdrawal, redeeming the excess rsETH for ETH that belonged to existing holders.
6. No admin action or special role is required; the entry path is the public `depositAsset()` function. [1](#0-0) [6](#0-5)

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

**File:** contracts/LRTOracle.sol (L249-250)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
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
