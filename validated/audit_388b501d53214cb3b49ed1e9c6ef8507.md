### Title
Stale Chainlink Price in `ChainlinkPriceOracle` Allows Depositing Depegging LSTs at Inflated Rates, Causing Protocol Insolvency - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price via `latestRoundData()` but silently discards the `updatedAt` timestamp, performing no staleness validation. When a supported LST (stETH, rETH, ETHx, swETH) depegs on the market while the Chainlink feed lags behind, any unprivileged depositor can call `LRTDepositPool.depositAsset()` with the depegging LST and receive rsETH calculated at the stale (inflated) oracle price. This mints more rsETH than the deposited collateral is worth, diluting all existing rsETH holders and driving the protocol toward insolvency.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads the Chainlink feed as follows:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

The `updatedAt` and `answeredInRound` return values are discarded entirely. No heartbeat or round-completeness check is performed. This is the oracle used by `LRTOracle.getAssetPrice()`, which is in turn consumed by `LRTDepositPool.getRsETHAmountToMint()`:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

The `rsETHPrice` stored in `LRTOracle` is a cached value updated only when `updateRSETHPrice()` is called. The minting ratio is therefore entirely dependent on the Chainlink feed being current.

By contrast, the pool-level oracle `ChainlinkOracleForRSETHPoolCollateral` does perform a round-completeness check (`answeredInRound < roundID`), demonstrating the protocol is aware of the pattern but failed to apply it to the primary deposit path.

---

### Impact Explanation

**Protocol insolvency (Critical).**

When an LST depegs (e.g., stETH trades at 0.95 ETH on the market while the Chainlink feed still reports 1.00 ETH):

1. An attacker deposits 1,000 stETH (market value: 950 ETH) via `depositAsset()`.
2. `getRsETHAmountToMint()` prices stETH at 1.00 ETH per the stale feed, minting rsETH worth 1,000 ETH.
3. The attacker extracts 50 ETH of value from existing rsETH holders.
4. When `updateRSETHPrice()` is eventually called with the correct stETH price, `_getTotalEthInProtocol()` computes a lower TVL, the new `rsETHPrice` drops, and all existing holders are diluted.
5. Repeated at scale, the protocol's backing collapses below 1:1, making rsETH insolvent.

The `_getTotalEthInProtocol()` function in `LRTOracle` also calls `getAssetPrice()` for every supported asset when computing the rsETH price update, meaning the stale price propagates into the TVL calculation as well.

---

### Likelihood Explanation

LST depeg events are not hypothetical — stETH traded at a significant discount to ETH during the 2022 Celsius/3AC crisis, and Chainlink feeds for LSTs have heartbeats of 24 hours (or update only on 0.5% deviation). During a rapid depeg, the feed can lag the market by minutes to hours. Any MEV bot or informed trader monitoring the spread between the Chainlink feed and DEX spot price can profitably exploit this window. The entry path (`depositAsset`) is fully permissionless with no access control.

---

### Recommendation

Add a staleness check in `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();
    require(answeredInRound >= roundId, "Stale price");
    require(updatedAt != 0, "Incomplete round");
    require(block.timestamp - updatedAt <= MAX_STALENESS, "Price too old");
    require(price > 0, "Invalid price");
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`MAX_STALENESS` should be set per-asset based on the Chainlink feed's documented heartbeat (e.g., 3600 seconds for a 1-hour heartbeat feed).

---

### Proof of Concept

1. Observe stETH/ETH Chainlink feed is stale at 1.00 ETH while market price is 0.95 ETH (5% depeg).
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 10_000e18, 0, "")`.
3. `getRsETHAmountToMint()` computes: `(10_000e18 * 1e18) / rsETHPrice`. With rsETHPrice ≈ 1.02e18 (accumulated yield), attacker receives ≈ 9,804 rsETH.
4. True ETH value deposited: 9,500 ETH. rsETH minted represents ≈ 9,804 × 1.02 = 10,000 ETH of claim.
5. Attacker immediately calls `LRTWithdrawalManager.initiateWithdrawal(ETH, 9804e18, "")` to queue withdrawal of ETH.
6. When `updateRSETHPrice()` is called with the correct stETH price, TVL drops, rsETHPrice falls, and all other holders bear the loss.

**Key files and lines:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
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
