### Title
Stale Chainlink Price Accepted Without Staleness Validation Leads to Incorrect rsETH Minting — (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards all validity fields (`updatedAt`, `answeredInRound`, `roundId`). A stale price returned by Chainlink is accepted as-is and propagated directly into rsETH mint calculations, allowing depositors to receive more rsETH than their deposit is worth and diluting existing rsETH holders.

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price feed but only reads the `price` field:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L52-54
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The returned tuple is `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The contract discards:
- `updatedAt` — the timestamp of the last price update (staleness check)
- `answeredInRound` — whether the answer was computed in the current round (completeness check)

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` (used in the L2 pool system) does perform these checks:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L27-32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
```

The stale price from `ChainlinkPriceOracle` flows into `LRTOracle.getAssetPrice()` → `LRTOracle._getTotalEthInProtocol()` → `LRTOracle._updateRsETHPrice()`, and also directly into `LRTDepositPool.getRsETHAmountToMint()`:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

If the stale price is higher than the true market price (e.g., Chainlink has not updated during a price drop), a depositor receives more rsETH than their deposit is worth. The rsETH minted in excess is backed by fewer real assets than implied, directly diluting the value held by all existing rsETH holders.

### Impact Explanation

**High — Theft of unclaimed yield.**

When a stale inflated price is used:
- `getAssetPrice(asset)` returns a value above the true rate
- `getRsETHAmountToMint` mints excess rsETH to the depositor
- The excess rsETH is unbacked; its value is extracted from the pool of existing rsETH holders

Existing holders' share of the underlying TVL is permanently diluted by the over-minted rsETH. This constitutes theft of yield accrued by existing stakers.

### Likelihood Explanation

**Medium.** Chainlink price feeds have a heartbeat (e.g., 1 hour for stETH/ETH on mainnet) and a deviation threshold. During periods of low volatility, the feed may not update for the full heartbeat window. If the true price drops within that window, the stale (higher) price remains on-chain and is accepted without any check. No privileged access is required; any depositor can observe the on-chain `updatedAt` timestamp and time a deposit accordingly.

### Recommendation

Add staleness and completeness checks in `ChainlinkPriceOracle.getAssetPrice()`, consistent with what `ChainlinkOracleForRSETHPoolCollateral` already does:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Stale price");
require(updatedAt != 0, "Incomplete round");
require(block.timestamp - updatedAt <= MAX_STALENESS, "Price too old");
require(price > 0, "Invalid price");
```

`MAX_STALENESS` should be set per-asset based on the Chainlink heartbeat for that feed.

### Proof of Concept

1. Chainlink stETH/ETH feed last updated at `T=0` with price `1.06 ETH`. True price at `T=3600` is `1.04 ETH` (price dropped, but heartbeat has not triggered an update yet).
2. `LRTOracle.rsETHPrice` was last set correctly at `1.05 ETH` (from a prior `updateRSETHPrice()` call).
3. Attacker calls `LRTDepositPool.depositAsset(stETH, 1e18, 0, "")`.
4. `getRsETHAmountToMint(stETH, 1e18)` computes:
   - `getAssetPrice(stETH)` → `ChainlinkPriceOracle` returns stale `1.06e18`
   - `rsETHPrice()` → `1.05e18`
   - `rsethAmountToMint = 1e18 * 1.06e18 / 1.05e18 ≈ 1.0095e18`
5. Attacker receives `~1.0095 rsETH` for `1 stETH` worth `1.04 ETH` at true price. The `~0.0095 rsETH` excess is unbacked and dilutes all existing rsETH holders. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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
