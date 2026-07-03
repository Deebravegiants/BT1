### Title
`ChainlinkPriceOracle` Accepts Stale/Invalid Prices Without Validation, Enabling Incorrect rsETH Minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all validity metadata (`updatedAt`, `answeredInRound`, `roundId`), accepting stale or incomplete Chainlink rounds without any check. This stale price flows through the publicly callable `LRTOracle.updateRSETHPrice()` into the stored `rsETHPrice`, which directly governs how much rsETH is minted per deposited asset in `LRTDepositPool.getRsETHAmountToMint()`. No outlier filtering or circuit-breaker exists to prevent a malfunction-era price from being committed on-chain and used for minting.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads only the raw `price` field from `latestRoundData()`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

It silently ignores `roundId`, `updatedAt`, and `answeredInRound`. There is no check for:
- `answeredInRound < roundId` (stale round)
- `updatedAt == 0` (incomplete round)
- `price <= 0` (invalid price)
- `block.timestamp - updatedAt > heartbeat` (time-based staleness)

The protocol's own `ChainlinkOracleForRSETHPoolCollateral` (used for L2 pool collateral) performs all three structural checks:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L27-36
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The stale price from `ChainlinkPriceOracle` propagates through the following call chain:

1. `LRTOracle.getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice(asset)` (stale price returned)
2. `LRTOracle._getTotalEthInProtocol()` uses the stale price to compute `totalETHInProtocol`
3. `LRTOracle._updateRsETHPrice()` computes `newRsETHPrice = totalETHInProtocol / rsethSupply` using the stale TVL
4. `LRTOracle.updateRSETHPrice()` is **publicly callable** with no role restriction — any address can commit the stale price on-chain
5. `LRTDepositPool.getRsETHAmountToMint()` uses the now-incorrect `lrtOracle.rsETHPrice()` to determine how many rsETH tokens to mint per deposit

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

The `pricePercentageLimit` guard in `_updateRsETHPrice()` provides partial mitigation only when:
- It has been explicitly set by admin (defaults to `0`, meaning **no protection**)
- The stale price deviation exceeds the configured threshold

A stale price within the threshold — or any price when `pricePercentageLimit == 0` — is committed unconditionally.

---

### Impact Explanation

**High — Theft of unclaimed yield / dilution of existing rsETH holders.**

If a Chainlink LST/ETH feed goes stale at a price lower than the true market price (e.g., during a network outage or extreme volatility event):

- `_getTotalEthInProtocol()` underestimates the protocol's TVL
- `rsETHPrice` is set below its true value
- `getRsETHAmountToMint = (amount × assetPrice) / rsETHPrice` yields **more rsETH than the depositor is entitled to**
- The excess rsETH represents value extracted from existing rsETH holders (their share of the pool is diluted)
- The attacker can immediately redeem or sell the excess rsETH

Conversely, if the stale price is inflated, depositors receive fewer rsETH tokens than they are owed — a direct loss to the depositor.

---

### Likelihood Explanation

**Medium.** Chainlink feeds do go stale during network congestion, oracle node failures, or extreme market events. The attack requires no special privilege: `updateRSETHPrice()` is publicly callable. An attacker monitoring Chainlink round data can detect a stale round and immediately call `updateRSETHPrice()` followed by a deposit in the same block, atomically locking in the favorable rate before the oracle recovers.

---

### Recommendation

Apply the same validation pattern already used in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    if (block.timestamp - updatedAt > MAX_STALENESS_PERIOD) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, ensure `pricePercentageLimit` is set to a non-zero value at deployment so the `_updateRsETHPrice()` circuit-breaker is active.

---

### Proof of Concept

1. A Chainlink LST/ETH price feed (e.g., stETH/ETH) goes stale — `answeredInRound < roundId` — with the last committed price 5% below the true market price.
2. Attacker calls `LRTOracle.updateRSETHPrice()` (no access control, `public whenNotPaused`).
3. `_getTotalEthInProtocol()` calls `getAssetPrice(stETH)` via `ChainlinkPriceOracle`, which returns the stale low price without reverting.
4. `rsETHPrice` is set ~5% below its true value and stored on-chain.
5. Attacker calls `LRTDepositPool.depositAsset(stETH, amount, minRSETHAmountExpected, "")`.
6. `getRsETHAmountToMint = (amount × staleAssetPrice) / staleRsETHPrice` — because both numerator and denominator use the same stale feed, the effect partially cancels for the deposited asset. However, if the attacker deposits ETH (priced at `1e18` via `OneETHPriceOracle`) while only the stETH feed is stale, the denominator `rsETHPrice` is depressed but the numerator `getAssetPrice(ETH) = 1e18` is unaffected, yielding a net over-mint.
7. Attacker receives more rsETH than their ETH deposit is worth at the true exchange rate, diluting all existing rsETH holders. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-267)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

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

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
