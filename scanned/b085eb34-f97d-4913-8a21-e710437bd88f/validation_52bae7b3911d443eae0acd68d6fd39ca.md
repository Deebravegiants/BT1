### Title
Missing Chainlink Oracle Validation in `ChainlinkPriceOracle.getAssetPrice()` Enables Stale/Invalid Price Acceptance - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards `roundId`, `updatedAt`, and `answeredInRound`, performing no staleness, completeness, or sign checks on the returned price. This is the exact vulnerability class from the external report. Notably, the same codebase already implements all three checks correctly in `ChainlinkOracleForRSETHPoolCollateral`, confirming the protocol is aware of the requirement but omitted it from the core oracle.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the asset/ETH price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

Three validations are absent:

1. **No staleness check** — `answeredInRound >= roundId` is never verified. A round whose answer was carried over from a prior round (i.e., `answeredInRound < roundId`) is silently accepted.
2. **No incomplete-round check** — `updatedAt != 0` is never verified. A round that has not yet been completed returns `updatedAt == 0` and is silently accepted.
3. **No sign check** — `price > 0` is never verified. In Solidity 0.8, an explicit `uint256(negative_int256)` cast does **not** revert; it wraps to a near-`type(uint256).max` value.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` — used for pool collateral pricing in the same repository — performs all three checks:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [1](#0-0) [2](#0-1) 

---

### Impact Explanation

`ChainlinkPriceOracle.getAssetPrice(asset)` is the price source for every supported LST asset (stETH, rETH, etc.) in the protocol. It feeds into two critical paths:

**Path 1 — rsETH minting (deposit flow):**
`LRTDepositPool.getRsETHAmountToMint()` computes:
```
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()
```
A stale inflated asset price causes the depositor to receive more rsETH than their deposit is worth, diluting all existing rsETH holders. [3](#0-2) 

**Path 2 — rsETH price update:**
`LRTOracle._updateRsETHPrice()` calls `_getTotalEthInProtocol()`, which iterates over all supported assets and sums `totalAssetAmt * getAssetPrice(asset)`. A stale or wrapped-negative price inflates or deflates the computed TVL, causing `rsETHPrice` to be set incorrectly for all subsequent operations. [4](#0-3) [5](#0-4) 

**Path 3 — withdrawal calculations:**
`LRTWithdrawalManager` reads `lrtOracle.getAssetPrice(asset)` when computing unlock parameters for withdrawals, meaning stale prices also affect how much collateral a withdrawer receives. [6](#0-5) 

**Negative price wrap-around:** If Chainlink ever returns `price <= 0`, `uint256(price)` in Solidity 0.8 wraps to a value near `type(uint256).max`, making `totalETHInProtocol` astronomically large. This would either trigger the `PriceAboveDailyThreshold` revert (freezing price updates) or, if the manager bypasses it, mint an unbounded amount of rsETH as protocol fee. [7](#0-6) 

**Impact classification:** High — theft of unclaimed yield / value from existing rsETH holders via stale-price-assisted over-minting; potential temporary freeze of price updates via wrapped negative price.

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat windows (e.g., 24 h on mainnet, 1 h on some L2s). During network congestion, sequencer downtime (L2), or a Chainlink node outage, the feed can go stale within its heartbeat window without triggering a deviation update. This is a well-known, historically observed condition. The protocol already acknowledges the risk by implementing the checks in `ChainlinkOracleForRSETHPoolCollateral`, making the omission in `ChainlinkPriceOracle` a clear inconsistency. Any depositor can exploit a stale price window permissionlessly.

---

### Recommendation

Apply the same three-check pattern already used in `ChainlinkOracleForRSETHPoolCollateral.getRate()` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    require(answeredInRound >= roundId, "Stale price");
    require(updatedAt != 0, "Incomplete round");
    require(price > 0, "Invalid price");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, consider adding a `block.timestamp - updatedAt <= MAX_STALENESS` check with a configurable heartbeat threshold per asset feed.

---

### Proof of Concept

1. Chainlink's ETH-denominated feed for a supported LST (e.g., stETH/ETH) enters a stale state — `answeredInRound < roundId` — due to a node outage. The last reported price is 1.05 ETH per stETH (above the true current value of 1.00 ETH).
2. An attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18)`.
3. `getRsETHAmountToMint` calls `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale `1.05e18` with no revert.
4. The attacker receives `1000 * 1.05e18 / rsETHPrice` rsETH — 5% more than the deposit is worth.
5. The attacker redeems the excess rsETH, extracting value from existing holders.
6. No special role or privilege is required; the entry point is the public `depositAsset` function. [1](#0-0) [2](#0-1)

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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

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

**File:** contracts/LRTWithdrawalManager.sol (L846-850)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
```
