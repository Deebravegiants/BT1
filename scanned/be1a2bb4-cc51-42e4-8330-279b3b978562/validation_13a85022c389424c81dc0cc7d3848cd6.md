### Title
Stale Chainlink Price Accepted Without Staleness Validation in `ChainlinkPriceOracle.getAssetPrice()`, Enabling Incorrect rsETH Exchange Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but discards the `updatedAt` timestamp and `answeredInRound` fields entirely. A stale Chainlink price is silently accepted and propagated into `LRTOracle._updateRsETHPrice()`, which sets the protocol-wide `rsETHPrice` used for all deposits and withdrawals. Any user can trigger this path by calling the public `LRTOracle.updateRSETHPrice()`.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the LST/ETH exchange rate from a Chainlink aggregator:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The return values `updatedAt` (timestamp of last update) and `answeredInRound` (round completeness indicator) are silently discarded. No maximum age check and no round-completeness check are performed.

This contrasts directly with `ChainlinkOracleForRSETHPoolCollateral.sol`, a sibling contract in the same repository, which correctly validates all three conditions:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The stale price flows through the following call chain:

1. `ChainlinkPriceOracle.getAssetPrice(asset)` — returns stale LST/ETH price
2. `LRTOracle.getAssetPrice(asset)` — delegates to the above
3. `LRTOracle._getTotalEthInProtocol()` — sums all asset values using stale prices
4. `LRTOracle._updateRsETHPrice()` — computes and stores `rsETHPrice` from the stale total
5. `LRTOracle.updateRSETHPrice()` — **publicly callable with no access restriction**

The stored `rsETHPrice` is then consumed by `LRTDepositPool` (to compute rsETH minted per deposit) and `LRTWithdrawalManager` (to compute ETH returned per rsETH burned).

---

### Impact Explanation

**Scenario A — Stale HIGH price (e.g., stETH depegs but Chainlink circuit breaker holds the price at 1.0):**
- `totalETHInProtocol` is inflated → `rsETHPrice` is inflated
- Withdrawers burn rsETH and receive more ETH than the protocol actually holds → direct theft of funds from other depositors
- Depositors receive fewer rsETH than they are entitled to

**Scenario B — Stale LOW price (e.g., Chainlink feed lags during a recovery):**
- `rsETHPrice` is deflated
- Depositors receive more rsETH than they should → dilution of existing rsETH holders
- Withdrawers receive less ETH than they are entitled to

Scenario A constitutes **direct theft of user funds at rest**, qualifying as Critical impact. Scenario B constitutes **permanent dilution of unclaimed yield**, qualifying as High impact.

---

### Likelihood Explanation

Chainlink feeds are known to go stale during extreme market events due to:
- Deviation-threshold-based update model (price must move >X% to trigger an update)
- Min/max circuit breakers that freeze the reported price at bounds during crashes
- Network congestion preventing timely on-chain updates

The stETH/ETH and similar LST feeds have historically exhibited staleness during depeg events. The trigger (`updateRSETHPrice()`) is publicly callable by any address, so an attacker can deliberately call it at the moment a stale price is most advantageous, then immediately withdraw.

---

### Recommendation

Apply the same staleness checks already present in `ChainlinkOracleForRSETHPoolCollateral.sol` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    if (block.timestamp - updatedAt > MAX_STALENESS_PERIOD) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

---

### Proof of Concept

1. Chainlink stETH/ETH feed goes stale at price `1.0e18` while the actual market price drops to `0.95e18` (5% depeg).
2. Attacker observes the stale feed on-chain.
3. Attacker calls `LRTOracle.updateRSETHPrice()` (no access restriction).
   - `_getTotalEthInProtocol()` uses the stale `1.0e18` stETH price → `totalETHInProtocol` is inflated by ~5%.
   - `rsETHPrice` is set ~5% above its true value.
4. Attacker immediately calls `LRTWithdrawalManager` to initiate a withdrawal, burning rsETH at the inflated `rsETHPrice`.
5. Attacker receives ~5% more ETH than the protocol's actual backing, extracting value from other depositors.

**Root cause line:** [1](#0-0) 

**Contrast with the correct implementation in the same repo:** [2](#0-1) 

**Public trigger (no access restriction):** [3](#0-2) 

**Stale price propagated into rsETH price computation:** [4](#0-3)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L27-36)
```text
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
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
