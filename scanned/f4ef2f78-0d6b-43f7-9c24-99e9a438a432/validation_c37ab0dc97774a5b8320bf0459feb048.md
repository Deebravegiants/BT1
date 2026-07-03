### Title
Unvalidated Chainlink Price Data in `ChainlinkPriceOracle` Enables Stale/Zero Price to Corrupt rsETH Minting and Price Updates - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` consumes Chainlink `latestRoundData()` output without validating staleness, round completeness, or price sign. This unvalidated price flows directly into rsETH minting amounts (`LRTDepositPool.getRsETHAmountToMint`) and the global rsETH price update (`LRTOracle.updateRSETHPrice`), both reachable by any unprivileged user. A stale or zero price causes depositors to receive incorrect rsETH amounts, constituting theft of yield from existing holders or loss of deposited assets.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` calls `priceFeed.latestRoundData()` and silently discards all validation fields, using only the raw `price` value:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol:52-54
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

No checks are performed for:
- `price <= 0` (zero or negative answer from a circuit-breaker or uninitialized feed)
- `updatedAt == 0` (incomplete round)
- `answeredInRound < roundId` (stale round)
- Heartbeat/timestamp age (feed has not been updated within the expected interval)

The same codebase already implements all three validations correctly in `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol:30-32
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The unvalidated price from `ChainlinkPriceOracle` propagates through two critical paths:

**Path 1 — Direct minting:**
`LRTDepositPool.getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(asset)` directly in the numerator of the mint calculation:
```solidity
// contracts/LRTDepositPool.sol:520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**Path 2 — Global price update (public):**
`LRTOracle.updateRSETHPrice()` is callable by anyone and internally calls `_getTotalEthInProtocol()`, which iterates over all supported LSTs and calls `getAssetPrice(asset)` for each:
```solidity
// contracts/LRTOracle.sol:339,343
uint256 assetER = getAssetPrice(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
The resulting `totalETHInProtocol` is then used to compute and persist `rsETHPrice`.

---

### Impact Explanation

**Stale price (most realistic):** If a Chainlink LST/ETH feed (e.g., stETH/ETH) goes stale during network congestion or sequencer downtime, the last known price is returned without any age check. If the stale price is higher than the true current price, `getAssetPrice` returns an inflated value, causing `getRsETHAmountToMint` to mint excess rsETH to the depositor. This excess dilutes the share of all existing rsETH holders — constituting theft of unclaimed yield.

**Zero price (circuit-breaker edge case):** If the feed returns `answer = 0`, then `getAssetPrice` returns `0`. In `getRsETHAmountToMint`, the numerator becomes zero, so `rsethAmountToMint = 0`. The depositor's LST tokens are transferred in (`safeTransferFrom` succeeds) but zero rsETH is minted — a permanent loss of deposited funds.

**Negative price cast to uint256:** A negative `int256` price cast to `uint256` produces an astronomically large value, inflating `totalETHInProtocol` and causing `_updateRsETHPrice` to compute an extreme `newRsETHPrice`, which would trigger the `PriceAboveDailyThreshold` revert for non-manager callers, effectively bricking public price updates.

---

### Likelihood Explanation

Chainlink feeds are generally reliable, but staleness is a documented and recurring risk during:
- L2 sequencer downtime (Arbitrum, Optimism, etc.)
- Extreme network congestion
- Chainlink node operator issues

The zero-price scenario is less common but possible when a feed is first deployed or during circuit-breaker activation. The public `updateRSETHPrice()` entry point means no privileged access is needed to trigger the corrupted price path. Likelihood is **Low** given Chainlink's reliability, but the impact is severe enough to warrant a High severity rating.

---

### Recommendation

Apply the same validation pattern already used in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    // Optionally: if (block.timestamp - updatedAt > HEARTBEAT_INTERVAL) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

---

### Proof of Concept

1. Chainlink stETH/ETH feed goes stale (e.g., last updated 4 hours ago, heartbeat is 1 hour). The feed still returns the last known price without reverting.
2. Anyone calls `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_getTotalEthInProtocol()` calls `getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale inflated price without any staleness check.
4. `totalETHInProtocol` is overstated; `newRsETHPrice` is set higher than the true value.
5. A depositor now calls `LRTDepositPool.depositAsset(stETH, amount)`, which calls `getRsETHAmountToMint(stETH, amount)`:
   ```solidity
   rsethAmountToMint = (amount * lrtOracle.getAssetPrice(stETH)) / lrtOracle.rsETHPrice();
   ```
   Both numerator and denominator are inflated by the same stale price, so in the symmetric case the effect cancels. However, if only the asset price is stale (not the rsETHPrice, which was set in a prior update cycle), the depositor receives more rsETH than their deposit warrants, stealing yield from existing holders.

**Zero-price scenario:**
1. Feed returns `answer = 0` for stETH/ETH.
2. `getAssetPrice(stETH)` returns `0`.
3. `getRsETHAmountToMint(stETH, 1e18)` = `(1e18 * 0) / rsETHPrice` = `0`.
4. Depositor's 1 stETH is transferred to the deposit pool; depositor receives 0 rsETH — funds permanently lost. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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
