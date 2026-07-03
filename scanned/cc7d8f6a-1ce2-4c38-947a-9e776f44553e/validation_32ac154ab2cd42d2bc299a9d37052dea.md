### Title
No Staleness Check or Fallback Oracle in `ChainlinkPriceOracle` Causes Protocol-Wide Revert on Feed Failure - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` with no staleness validation, no zero/negative price guard, and no fallback oracle. If the Chainlink feed reverts or returns invalid data (e.g., due to price history gaps, sequencer downtime, or feed deprecation), every protocol function that depends on asset prices — deposits, withdrawal initiations, and queue unlocking — reverts, temporarily freezing user funds.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` is the sole price source for all supported LST assets in the protocol. It calls `latestRoundData()` and blindly casts the result with no validation:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

There is no check on `updatedAt` (staleness), no check that `price > 0`, no check that `answeredInRound >= roundId`, and no fallback oracle. Compare this to `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which does validate `answeredInRound < roundID`, `timestamp == 0`, and `ethPrice <= 0` — but that contract is only used for pool collateral, not for the core `LRTOracle`. [1](#0-0) 

If the Chainlink feed reverts (e.g., due to price history gaps, sequencer downtime, or feed deprecation), `getAssetPrice()` propagates the revert up through the entire call chain:

1. `LRTOracle.getAssetPrice(asset)` → delegates to `IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset)` [2](#0-1) 
2. `LRTOracle._getTotalEthInProtocol()` → calls `getAssetPrice(asset)` for every supported asset in a loop [3](#0-2) 
3. `LRTOracle._updateRsETHPrice()` → calls `_getTotalEthInProtocol()` [4](#0-3) 
4. `LRTDepositPool.getRsETHAmountToMint()` → calls `lrtOracle.getAssetPrice(asset)`, blocking all deposits [5](#0-4) 
5. `LRTWithdrawalManager.getExpectedAssetAmount()` → calls `lrtOracle.getAssetPrice(asset)`, blocking `initiateWithdrawal()` [6](#0-5) 
6. `LRTWithdrawalManager._createUnlockParams()` → calls `lrtOracle.getAssetPrice(asset)`, blocking `unlockQueue()` [7](#0-6) 

### Impact Explanation
**Medium — Temporary freezing of funds.** When any supported asset's Chainlink feed becomes unavailable or reverts, all deposits, all new withdrawal initiations, and all `unlockQueue()` calls revert. Users who have already queued withdrawals cannot have their requests processed until the feed recovers. There is no reserve oracle to fall back to, so the protocol is entirely dependent on Chainlink feed liveness.

### Likelihood Explanation
Chainlink feeds are known to experience temporary outages (sequencer downtime on L2, price history gaps during high volatility, feed deprecation). The protocol supports multiple LST assets (stETH, ETHx, rETH, sfrxETH, swETH), each with its own Chainlink feed — any single feed failure blocks the entire protocol. This is a realistic and documented failure mode.

### Recommendation
1. Add staleness and validity checks to `ChainlinkPriceOracle.getAssetPrice()` (check `updatedAt`, `answeredInRound >= roundId`, and `price > 0`), mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral.getRate()`. [8](#0-7) 
2. Add a fallback/reserve price oracle per asset in `LRTOracle` (e.g., a secondary on-chain rate source or a manually-set guardian price), so that if the primary Chainlink feed reverts, the fallback is used instead of propagating the revert.
3. Consider wrapping the `getAssetPrice()` call in `_getTotalEthInProtocol()` with a try/catch that falls back to the reserve oracle, preventing a single feed failure from blocking all protocol operations.

### Proof of Concept
1. Chainlink feed for stETH/ETH becomes temporarily unavailable and `latestRoundData()` reverts.
2. Any user calls `LRTDepositPool.depositAsset(stETH, amount, minRSETH)`.
3. `depositAsset` → `_beforeDeposit` → `getRsETHAmountToMint` → `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → `priceFeed.latestRoundData()` reverts.
4. The deposit reverts. Simultaneously, any operator calling `unlockQueue(stETH, ...)` also reverts via the same path through `_createUnlockParams` → `lrtOracle.getAssetPrice(stETH)`.
5. All queued stETH withdrawals are frozen until the Chainlink feed recovers. There is no reserve oracle to substitute. [1](#0-0) [9](#0-8) [10](#0-9)

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

**File:** contracts/LRTOracle.sol (L231-231)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();
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

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L837-851)
```text
    function _createUnlockParams(
        ILRTOracle lrtOracle,
        ILRTUnstakingVault unstakingVault,
        address asset
    )
        internal
        view
        returns (UnlockParams memory)
    {
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
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
