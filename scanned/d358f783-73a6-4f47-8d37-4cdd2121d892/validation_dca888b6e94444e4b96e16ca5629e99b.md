### Title
Chainlink Oracle Downtime or Zero Price Freezes All Deposits and Withdrawal Initiations - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` with no staleness check, no zero/negative price guard, and no try/catch. If Chainlink pauses or deprecates a feed for any supported LST asset, every user-facing operation that depends on that price — deposits, withdrawal initiations, and instant withdrawals — reverts and is frozen for all users.

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the price with a bare call:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

There is no check that `price > 0`, no `updatedAt` staleness guard, and no `try/catch` around the external call. [1](#0-0) 

Compare this to `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which does validate `answeredInRound`, `timestamp`, and `ethPrice > 0` — demonstrating the project is aware of these checks but omitted them in the primary oracle. [2](#0-1) 

This unguarded call propagates into three critical user-facing paths:

**1. Deposit path**

`depositAsset()` / `depositETH()` → `_beforeDeposit()` → `getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(asset)`, which delegates to `ChainlinkPriceOracle.getAssetPrice()`. If the feed reverts, the entire deposit reverts. [3](#0-2) 

**2. Withdrawal initiation path**

`initiateWithdrawal()` calls `getExpectedAssetAmount(asset, rsETHUnstaked)`, which calls `lrtOracle.getAssetPrice(asset)`. A reverted feed freezes all new withdrawal requests. [4](#0-3) 

`getExpectedAssetAmount` directly calls `lrtOracle.getAssetPrice(asset)` with no fallback. [5](#0-4) 

**3. Instant withdrawal path**

`instantWithdrawal()` also calls `getExpectedAssetAmount()` before burning rsETH, so users cannot redeem rsETH instantly either. [6](#0-5) 

**4. Price update path**

`updateRSETHPrice()` → `_getTotalEthInProtocol()` iterates all supported assets and calls `getAssetPrice(asset)` for each. A single failing feed blocks the rsETH price update, which in turn makes `rsETHPrice` stale and can cause `getRsETHAmountToMint` to use an outdated denominator. [7](#0-6) 

### Impact Explanation

If Chainlink pauses or deprecates a price feed for any supported LST (as it did for UST/ETH during the Terra collapse), every call to `depositAsset`, `depositETH`, `initiateWithdrawal`, and `instantWithdrawal` for that asset reverts. Users holding rsETH backed by that asset cannot initiate redemptions. This constitutes a **temporary (potentially permanent) freezing of user funds** — matching the Critical/Medium impact tier.

### Likelihood Explanation

Chainlink has a documented history of pausing feeds during extreme market events. The protocol supports multiple LST assets (stETH, ETHx, etc.), each with its own Chainlink feed. Any single feed going offline triggers the freeze. This is a realistic, precedented scenario.

### Recommendation

1. Wrap `latestRoundData()` in a `try/catch` and revert with a descriptive error rather than propagating the Chainlink revert.
2. Add a staleness check: `if (block.timestamp - updatedAt > maxDelay) revert StalePrice()`.
3. Add a zero/negative price check: `if (price <= 0) revert InvalidPrice()`.
4. Consider a circuit-breaker fallback price or a secondary oracle so that a single feed failure does not freeze all protocol operations.

### Proof of Concept

1. Chainlink pauses the stETH/ETH feed (as it has done for other assets historically). `AggregatorV3Interface.latestRoundData()` begins reverting.
2. Any user calls `depositAsset(stETH, amount, minRSETH, "")`.
3. Execution reaches `getRsETHAmountToMint` → `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → `priceFeed.latestRoundData()` → **reverts**.
4. The deposit reverts. All subsequent deposits for stETH are frozen.
5. Simultaneously, any user calling `initiateWithdrawal(stETH, rsETHAmount, "")` hits the same revert at `getExpectedAssetAmount` → `lrtOracle.getAssetPrice(stETH)`.
6. Users holding rsETH backed by stETH cannot initiate new withdrawals or use instant withdrawal, and their funds are effectively frozen until the feed is restored or an admin manually swaps the oracle.

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

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L168-170)
```text
        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
```

**File:** contracts/LRTWithdrawalManager.sol (L228-229)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
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
