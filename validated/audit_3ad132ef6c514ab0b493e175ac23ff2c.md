### Title
Missing Chainlink Staleness Validation in `ChainlinkPriceOracle.getAssetPrice()` While `ChainlinkOracleForRSETHPoolCollateral` Properly Validates — (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` fetches Chainlink prices without any staleness or validity checks. A sibling oracle contract in the same repository, `ChainlinkOracleForRSETHPoolCollateral`, performs all three required checks (`answeredInRound < roundID`, `timestamp == 0`, `ethPrice <= 0`). The stale prices returned by `ChainlinkPriceOracle` flow directly into `LRTOracle._updateRsETHPrice()`, corrupting the rsETH/ETH exchange rate used for minting and withdrawals.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards all validity fields:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();   // updatedAt, answeredInRound ignored
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

In contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same codebase performs all three guards:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L26-37
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

`ChainlinkPriceOracle` is registered as the `assetPriceOracle` for supported LST assets via `LRTOracle.updatePriceOracleFor()`. Its output is consumed by `LRTOracle.getAssetPrice()`, which is called inside `LRTOracle._getTotalEthInProtocol()`:

```solidity
// contracts/LRTOracle.sol L336-343
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);          // ← stale price accepted here
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    ...
}
```

`_getTotalEthInProtocol()` is called by `_updateRsETHPrice()`, which computes and stores `rsETHPrice`. That stored value is then used by:

- `LRTDepositPool.getRsETHAmountToMint()` — determines how many rsETH tokens a depositor receives:
  ```solidity
  // contracts/LRTDepositPool.sol L520
  rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
  ```
- `LRTWithdrawalManager.getExpectedAssetAmount()` — determines how many LSTs a withdrawer receives:
  ```solidity
  // contracts/LRTWithdrawalManager.sol L593
  underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
  ```

---

### Impact Explanation

**Impact: High — Theft of unclaimed yield from existing rsETH holders.**

If a Chainlink feed for a supported LST (e.g., stETH/ETH, ETHx/ETH) goes stale and returns a price lower than the true current price, `_updateRsETHPrice()` computes a deflated `rsETHPrice`. A depositor calling `depositETH` or `depositAsset` at that moment receives more rsETH than their deposit is worth (because the denominator `rsETHPrice` is artificially low). This over-minting dilutes the share of all existing rsETH holders, effectively transferring their accrued yield to the new depositor. The protocol's fee mechanism (`protocolFeeInBPS`) also misfires because `totalETHInProtocol` is understated, suppressing fee accrual.

---

### Likelihood Explanation

**Likelihood: Medium.**

Chainlink feeds for LSTs on Ethereum mainnet have heartbeat intervals (typically 1–24 hours) and deviation thresholds. During periods of network congestion, oracle node downtime, or sequencer issues on L2, feeds can lag or freeze. The `ChainlinkPriceOracle` has no circuit-breaker to detect this condition, while `ChainlinkOracleForRSETHPoolCollateral` does. A sophisticated actor monitoring mempool oracle updates can time a large deposit to coincide with a stale feed window.

---

### Recommendation

Apply the same three guards used in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();
    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, consider adding a configurable `maxStaleness` threshold (e.g., 24 hours) and reverting if `block.timestamp - updatedAt > maxStaleness`.

---

### Proof of Concept

1. Assume `stETH/ETH` Chainlink feed is configured in `ChainlinkPriceOracle` for the `stETH` asset.
2. The feed goes stale and returns a price of `0.95e18` (stETH/ETH) while the true price is `1.00e18`.
3. A keeper (or anyone) calls `LRTOracle.updateRSETHPrice()`.
4. `_getTotalEthInProtocol()` calls `getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice()` → returns `0.95e18` without reverting.
5. `totalETHInProtocol` is understated by 5% of the stETH TVL.
6. `newRsETHPrice` is computed lower than the true price and stored as `rsETHPrice`.
7. Attacker calls `LRTDepositPool.depositAsset(stETH, largeAmount, ...)`.
8. `getRsETHAmountToMint()` divides by the deflated `rsETHPrice`, minting excess rsETH to the attacker.
9. When the feed recovers and `updateRSETHPrice()` is called again, `rsETHPrice` rises, and the attacker's rsETH is now worth more than deposited — at the expense of existing holders' yield.

**Key code references:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTOracle.sol (L214-250)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

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

**File:** contracts/LRTWithdrawalManager.sol (L580-594)
```text
    function getExpectedAssetAmount(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 underlyingToReceive)
    {
        // setup oracle contract
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
