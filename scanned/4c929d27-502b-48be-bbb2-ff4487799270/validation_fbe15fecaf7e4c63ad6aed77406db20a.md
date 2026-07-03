### Title
`ChainlinkPriceOracle.getAssetPrice()` Uses Stale Chainlink Prices Without Staleness Validation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `price`, performing no staleness check. This stale price propagates into rsETH minting, withdrawal calculations, and the rsETH price update, enabling share mis-accounting exploitable by any unprivileged depositor or withdrawer.

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
```

The `roundId`, `updatedAt`, and `answeredInRound` return values are all silently discarded. [1](#0-0) 

`LRTOracle.getAssetPrice()` delegates directly to this fetcher with no additional validation: [2](#0-1) 

This stale price then flows into three critical paths:

**1. rsETH minting** — `LRTDepositPool.getRsETHAmountToMint()` uses `lrtOracle.getAssetPrice(asset)` to compute how many rsETH tokens to mint per deposited LST: [3](#0-2) 

Called from `_beforeDeposit()`, which is invoked by the public `depositAsset()` and `depositETH()`: [4](#0-3) 

**2. Withdrawal amount calculation** — `LRTWithdrawalManager.getExpectedAssetAmount()` uses `lrtOracle.getAssetPrice(asset)` to compute how much LST a user receives for their rsETH, called from the public `initiateWithdrawal()` and `instantWithdrawal()`: [5](#0-4) 

**3. rsETH price update** — `LRTOracle._getTotalEthInProtocol()` calls `getAssetPrice(asset)` for every supported asset to compute total protocol TVL, which drives `rsETHPrice` and fee minting: [6](#0-5) 

The protocol's own `ChainlinkOracleForRSETHPoolCollateral` demonstrates awareness of the issue by implementing partial staleness checks (`answeredInRound < roundID`, `timestamp == 0`), yet the core `ChainlinkPriceOracle` used for all LST pricing performs none of these: [7](#0-6) 

### Impact Explanation

**Impact: Medium — share/asset mis-accounting leading to incorrect rsETH minting and withdrawal amounts.**

If a Chainlink feed goes stale at a price above the true market price, a depositor calling `depositAsset()` receives more rsETH than their deposit warrants, diluting all existing rsETH holders. If stale at a price below true market, depositors receive fewer rsETH than deserved. In the withdrawal path, a stale-low asset price causes `getExpectedAssetAmount()` to return more LST than the rsETH is worth, allowing a withdrawer to extract excess value. Additionally, a stale price fed into `_updateRsETHPrice()` corrupts `rsETHPrice` and can trigger incorrect fee minting or false price-drop pauses.

### Likelihood Explanation

**Likelihood: Medium.**

Chainlink feeds have documented heartbeat intervals (e.g., 24 hours for ETH/stETH). During network congestion, oracle node outages, or low-volatility periods, feeds can remain at their last reported value well past the heartbeat. No heartbeat or `updatedAt` check exists anywhere in `ChainlinkPriceOracle`. Any user can trigger the vulnerable paths permissionlessly at any time.

### Recommendation

In `ChainlinkPriceOracle.getAssetPrice()`, validate all staleness indicators returned by `latestRoundData()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    if (block.timestamp - updatedAt > STALENESS_THRESHOLD) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

The `STALENESS_THRESHOLD` should be set per-feed based on its documented heartbeat interval.

### Proof of Concept

1. Chainlink's stETH/ETH feed goes stale (last update was 25 hours ago at price `0.999e18`; true price is now `0.990e18`).
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
3. `_beforeDeposit` → `getRsETHAmountToMint` → `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` returns stale `0.999e18` instead of true `0.990e18`.
4. Attacker receives `(1000e18 * 0.999e18) / rsETHPrice` rsETH — approximately 0.9% more than deserved.
5. Attacker redeems rsETH after the feed updates, extracting value from existing holders.

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

**File:** contracts/LRTOracle.sol (L336-344)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L648-665)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
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
