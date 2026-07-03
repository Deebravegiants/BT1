### Title
Single Failing Asset Price Oracle Blocks All rsETH Price Updates and Protocol Fee Collection - (`contracts/LRTOracle.sol`)

---

### Summary

`LRTOracle._getTotalEthInProtocol()` iterates over every supported asset and calls the external `IPriceFetcher` oracle for each one without any try-catch protection. If any single asset's third-party price oracle reverts, the entire `updateRSETHPrice()` call reverts, permanently blocking rsETH price updates and protocol fee collection for all assets.

---

### Finding Description

`LRTOracle._getTotalEthInProtocol()` is a private function called by `_updateRsETHPrice()`, which is in turn called by the public `updateRSETHPrice()` and `updateRSETHPriceAsManager()` functions. [1](#0-0) 

Inside the loop, `getAssetPrice(asset)` is called for every supported asset: [2](#0-1) 

`getAssetPrice` delegates to an external `IPriceFetcher` contract — for example, `ChainlinkPriceOracle.getAssetPrice()` calls `priceFeed.latestRoundData()` on a Chainlink aggregator: [3](#0-2) 

And `RETHPriceOracle.getAssetPrice()` calls `IrETH(rETHAddress).getExchangeRate()` on the rETH token contract: [4](#0-3) 

Neither call is wrapped in a try-catch. If any one of these external calls reverts — due to a deprecated Chainlink feed, a paused or upgraded underlying protocol contract, or any other third-party failure — the entire `_getTotalEthInProtocol()` call reverts, which causes `_updateRsETHPrice()` to revert, which causes `updateRSETHPrice()` to revert.

The protocol fee is minted exclusively inside `_updateRsETHPrice()`: [5](#0-4) 

And the price protection auto-pause logic also lives there: [6](#0-5) 

There is no alternative path to update `rsETHPrice` or collect fees if this function is blocked.

---

### Impact Explanation

**Permanent freezing of unclaimed yield (protocol fees):** Protocol fees are minted as rsETH inside `_updateRsETHPrice()`. If this function is permanently blocked by a single failing oracle, all accrued protocol fees are frozen indefinitely — no fee can be minted to the treasury.

**Stale rsETH price:** The stored `rsETHPrice` value used by `LRTDepositPool.getRsETHAmountToMint()` and `LRTWithdrawalManager.getExpectedAssetAmount()` becomes permanently stale, causing all depositors and withdrawers to receive incorrect amounts based on an outdated exchange rate. [7](#0-6) 

**Price protection disabled:** The auto-pause mechanism that triggers when rsETH price drops too far cannot fire, removing a critical safety net.

---

### Likelihood Explanation

Chainlink's `latestRoundData()` is documented to revert in certain conditions (e.g., when a feed is deprecated, when the L2 sequencer is down, or when the aggregator is paused). The rETH `getExchangeRate()` call depends on the Rocket Pool protocol, which could be paused or upgraded. The protocol supports multiple assets, so the attack surface grows with each added asset oracle. No admin action is required to trigger this — it occurs automatically if any third-party oracle enters a reverted state.

---

### Recommendation

Wrap each `getAssetPrice(asset)` call inside `_getTotalEthInProtocol()` in a try-catch block. If an oracle reverts, skip that asset's contribution (or use a cached/fallback price) and emit an event, rather than reverting the entire price update:

```solidity
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    try IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset) returns (uint256 assetER) {
        uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
        totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    } catch {
        emit AssetPriceOracleFailed(asset);
        // optionally use last known price or skip
    }
    unchecked { ++assetIdx; }
}
```

---

### Proof of Concept

1. Protocol has two supported assets: ETH and rETH.
2. The rETH oracle (`RETHPriceOracle`) calls `IrETH(rETHAddress).getExchangeRate()`.
3. Rocket Pool upgrades or pauses the rETH contract, causing `getExchangeRate()` to revert.
4. Any call to `updateRSETHPrice()` now reverts at `_getTotalEthInProtocol()` → `getAssetPrice(rETH)` → `getExchangeRate()`.
5. `rsETHPrice` is frozen at its last value. All protocol fees that would have been minted since the freeze are permanently lost. The price protection auto-pause cannot trigger. Depositors receive rsETH at a stale rate.
6. Recovery requires admin intervention to remove the broken oracle via `updatePriceOracleFor()`, but until that happens all fee yield is frozen. [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
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

**File:** contracts/LRTOracle.sol (L299-311)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
        } else {
            _checkAndUpdateDailyFeeMintLimit(0);
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

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/oracles/RETHPriceOracle.sol (L34-40)
```text
    function getAssetPrice(address asset) external view returns (uint256) {
        if (asset != rETHAddress) {
            revert InvalidAsset();
        }

        return IrETH(rETHAddress).getExchangeRate();
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
