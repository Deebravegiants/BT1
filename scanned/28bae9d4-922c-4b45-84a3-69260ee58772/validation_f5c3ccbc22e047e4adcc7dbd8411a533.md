### Title
Missing Chainlink Price Staleness Validation Allows Stale Price Exploitation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards all validity fields (`roundId`, `startedAt`, `updatedAt`, `answeredInRound`), accepting whatever price Chainlink last stored regardless of how old it is. This stale price flows directly into rsETH minting and price-update logic, enabling an attacker to exploit a stale-price window to extract excess rsETH or to trigger an unwarranted protocol-wide pause.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink answer with a destructured call that discards every validity field:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

No check is made on `updatedAt` (heartbeat staleness), `answeredInRound >= roundId` (round completeness), or `price > 0`. The price returned is whatever Chainlink last committed, which may be hours or days old.

This oracle is the price source for every LST asset (stETH, ETHx, rETH, swETH, sfrxETH) registered in `LRTOracle.assetPriceOracle`. It is consumed in two critical paths:

**Path 1 – rsETH minting:**
`LRTDepositPool.getRsETHAmountToMint()` divides `amount * lrtOracle.getAssetPrice(asset)` by `lrtOracle.rsETHPrice()`. [2](#0-1) 

**Path 2 – rsETH price update:**
`LRTOracle._getTotalEthInProtocol()` multiplies each asset's total balance by `getAssetPrice(asset)` to compute the protocol TVL, which then sets `rsETHPrice`. [3](#0-2) 

By contrast, the pool-side oracle wrapper `ChainlinkOracleForRSETHPoolCollateral` does perform a round-completeness check (`answeredInRound < roundID`) but still omits a time-based heartbeat check, and it is not the oracle used for LST asset pricing in the core deposit/withdrawal flow. [4](#0-3) 

### Impact Explanation
**Scenario A – Stale high price (theft of yield, High severity):**
If a Chainlink LST/ETH feed stalls at a price above the true current rate (e.g., during network congestion or a market dislocation), `getRsETHAmountToMint` returns an inflated rsETH amount. An attacker who deposits during this window receives more rsETH than the deposited assets are worth, diluting all existing rsETH holders. This constitutes theft of unclaimed yield from current holders.

**Scenario B – Stale low price (temporary fund freeze, Medium severity):**
If the stale price is below the true rate, calling the public `updateRSETHPrice()` computes a `newRsETHPrice` that is artificially depressed. If the drop exceeds `pricePercentageLimit`, `_updateRsETHPrice()` automatically pauses `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle`, freezing all user deposits and withdrawals until an admin manually unpauses. [5](#0-4) 

### Likelihood Explanation
Chainlink price feeds have documented heartbeat intervals (e.g., 1 hour for stETH/ETH on mainnet, 24 hours for some feeds). During periods of high gas prices, network congestion, or Chainlink node issues, feeds can lag beyond their heartbeat. This is a realistic, recurring operational condition, not a theoretical edge case. Because `updateRSETHPrice()` is a public, permissionless function, any actor can trigger the price update at the worst possible moment once a feed goes stale. [6](#0-5) 

### Recommendation
Add staleness and validity checks in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

require(answeredInRound >= roundId, "Stale round");
require(updatedAt != 0, "Incomplete round");
require(price > 0, "Non-positive price");
require(block.timestamp - updatedAt <= HEARTBEAT_TIMEOUT, "Price too stale");
```

Each asset's feed should have its own `HEARTBEAT_TIMEOUT` constant matching the Chainlink-published heartbeat for that feed. Alternatively, store a per-feed `maxStaleness` mapping settable by the LRT manager.

### Proof of Concept
1. Observe that the stETH/ETH Chainlink feed has not updated for > 1 hour (heartbeat exceeded).
2. Call `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)`, which returns the stale (e.g., artificially low) price without any staleness revert.
4. `newRsETHPrice` is computed using the stale TVL.
5. If the stale price is low enough to exceed `pricePercentageLimit`, the protocol auto-pauses — all deposits and withdrawals are frozen until admin intervention.
6. Alternatively, if the stale price is high, an attacker calls `LRTDepositPool.depositAsset(stETH, amount, 0, "")` and receives `amount * staleHighPrice / rsETHPrice` rsETH — more than the fair share — at the expense of existing holders. [1](#0-0) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
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
