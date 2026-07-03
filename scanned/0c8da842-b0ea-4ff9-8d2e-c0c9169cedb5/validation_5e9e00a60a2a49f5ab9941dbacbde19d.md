### Title
Missing Chainlink Price Staleness Validation Enables Over-Minting of rsETH via Stale Asset Prices - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards the `updatedAt` and `answeredInRound` return values, providing zero staleness protection. This price is consumed directly in the deposit and withdrawal flows. An unprivileged depositor can exploit a stale, inflated Chainlink price to receive more rsETH than the deposited asset is worth, diluting all existing rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

`latestRoundData()` returns `(roundId, answer, startedAt, updatedAt, answeredInRound)`. Only `answer` (the price) is used. The `updatedAt` timestamp and `answeredInRound` are completely ignored. There is no check such as:

```solidity
require(updatedAt >= block.timestamp - MAX_STALENESS, "Stale price");
require(answeredInRound >= roundId, "Stale round");
```

This price is consumed by `LRTOracle.getAssetPrice()`: [2](#0-1) 

Which is called by `LRTDepositPool.getRsETHAmountToMint()`: [3](#0-2) 

Which is called by `_beforeDeposit()`, invoked by both `depositAsset()` and `depositETH()`: [4](#0-3) 

The rsETH mint amount is computed as:

```
rsethAmountToMint = (depositAmount * getAssetPrice(asset)) / rsETHPrice
``` [5](#0-4) 

If `getAssetPrice(asset)` returns a stale, inflated value (e.g., the feed has not updated for hours due to network congestion or sequencer downtime), the numerator is artificially large, and the depositor receives more rsETH than the asset is actually worth.

The same stale price is also used in `LRTWithdrawalManager.getExpectedAssetAmount()`: [6](#0-5) 

And in `_getTotalEthInProtocol()` inside `LRTOracle`, which computes the rsETH price itself: [7](#0-6) 

---

### Impact Explanation

When a Chainlink feed is stale and its last reported price is higher than the true current price, a depositor calling `depositAsset()` receives excess rsETH. Because rsETH is a share token representing a proportional claim on all protocol assets, over-minting dilutes every existing rsETH holder's share. This constitutes direct theft of value from existing holders. At scale (e.g., a major LST depeg event where the feed lags), the protocol can become insolvent: the total rsETH supply represents more ETH value than the protocol actually holds.

**Impact level**: High (theft of unclaimed yield / protocol insolvency risk).

---

### Likelihood Explanation

Chainlink feeds can go stale due to:
- Network congestion preventing heartbeat updates
- Sequencer downtime on L2 deployments (the pool contracts operate on L2 chains)
- Oracle node failures or circuit-breaker deviations

The `pricePercentageLimit` guard in `LRTOracle._updateRsETHPrice()` only protects the rsETH price update, not individual asset prices used during deposits. [8](#0-7) 

Any depositor can call `depositAsset()` permissionlessly whenever the pool is unpaused, making this exploitable without any special role.

---

### Recommendation

Add staleness validation in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();
    require(price > 0, "Invalid price");
    require(updatedAt >= block.timestamp - MAX_STALENESS_PERIOD, "Stale price");
    require(answeredInRound >= roundId, "Stale round");
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`MAX_STALENESS_PERIOD` should be set per-asset based on each feed's heartbeat (e.g., 3600 seconds for 1-hour heartbeat feeds, 86400 seconds for 24-hour feeds).

---

### Proof of Concept

1. Assume `wstETH/ETH` Chainlink feed last updated at `T-2h` with price `1.20 ETH`. True current price is `1.10 ETH` (feed is stale due to network congestion).
2. Attacker calls `LRTDepositPool.depositAsset(wstETH, 1000e18, 0, "")`.
3. `getRsETHAmountToMint(wstETH, 1000e18)` computes: `(1000e18 * 1.20e18) / rsETHPrice`.
4. With a fair rsETH price of `1.05 ETH`, attacker receives `≈1142 rsETH` instead of the correct `≈1047 rsETH`.
5. Attacker immediately initiates withdrawal, locking in `≈95 rsETH` of excess value extracted from existing holders.
6. The `pricePercentageLimit` guard does not trigger because it only applies when `updateRSETHPrice()` is called, not during individual deposits. [9](#0-8) [10](#0-9)

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

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
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

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L516-520)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L648-669)
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

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
