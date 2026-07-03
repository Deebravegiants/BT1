### Title
Stale Chainlink Price Accepted Without Staleness Validation in `ChainlinkPriceOracle.getAssetPrice()` — (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but silently discards every return value except `price`. No check is performed on `updatedAt`, `answeredInRound`, or `roundId`. This is the direct analog of using `getPriceUnsafe` in Pyth: the function can return an arbitrarily stale price with no protocol-level rejection. The stale price propagates into rsETH minting and withdrawal calculations, enabling incorrect share issuance that harms existing rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` is the production oracle adapter for all LST assets (stETH, rETH, ETHx, etc.) registered in `LRTOracle`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol  line 49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (, int256 price,,,) = priceFeed.latestRoundData();   // ← updatedAt, answeredInRound, roundId all discarded

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The contract captures only `answer` (`price`). The three staleness indicators — `updatedAt` (wall-clock freshness), `answeredInRound` (round completeness), and `roundId` (round identity) — are all thrown away.

Contrast this with the project's own `ChainlinkOracleForRSETHPoolCollateral`, which does perform partial staleness checks:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol  line 27-32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();

if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

`ChainlinkPriceOracle` has none of these guards.

The stale price returned by `getAssetPrice()` is consumed in two critical paths:

**Path 1 — rsETH minting** (`LRTDepositPool.getRsETHAmountToMint()`):
```solidity
// contracts/LRTDepositPool.sol  line 520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**Path 2 — rsETH price update** (`LRTOracle._getTotalEthInProtocol()`):
```solidity
// contracts/LRTOracle.sol  line 339-343
uint256 assetER = getAssetPrice(asset);
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**Path 3 — withdrawal sizing** (`LRTWithdrawalManager.getExpectedAssetAmount()`):
```solidity
// contracts/LRTWithdrawalManager.sol  line 593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

---

### Impact Explanation

**Stale-high price scenario (most dangerous):** If a Chainlink feed freezes at a price above the true market value (e.g., during oracle node failure or L2 sequencer downtime), a depositor calling `depositAsset()` receives more rsETH than the deposited collateral is actually worth. When `updateRSETHPrice()` is next called with the corrected price, `_getTotalEthInProtocol()` returns a lower value, causing `rsETHPrice` to drop. All existing rsETH holders are diluted — their share of the backing pool decreases. This constitutes theft of yield from existing holders.

**Stale-low price scenario:** Depositors receive fewer rsETH tokens than deserved; withdrawers receive more underlying than deserved. The protocol under-issues shares, harming depositors.

Impact: **High — Theft of unclaimed yield** (existing rsETH holders lose backing value when stale-inflated prices allow over-minting).

---

### Likelihood Explanation

Chainlink feeds can go stale due to:
- Oracle node failures or network congestion preventing timely updates
- L2 sequencer downtime (the protocol deploys on L2 chains via RSETHPool contracts)
- Chainlink's deviation-threshold model: feeds only update when price moves ≥ threshold OR heartbeat expires; during low-volatility periods the heartbeat window (often 24 h) can elapse

Likelihood: **Low** — requires a Chainlink feed to go stale, which is uncommon but documented and has occurred historically.

---

### Recommendation

Add staleness and validity checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > STALENESS_THRESHOLD) revert StalePrice(); // e.g. 24 h + buffer
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

A per-feed configurable `maxStaleness` mapping is preferable since different Chainlink feeds have different heartbeat intervals.

---

### Proof of Concept

1. Chainlink's stETH/ETH feed freezes at `1.05e18` (last valid price) while the true market rate drops to `1.00e18` due to a depeg event.
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 100e18)`.
3. `getRsETHAmountToMint()` computes: `(100e18 * 1.05e18) / rsETHPrice` → attacker receives ~5% more rsETH than deserved.
4. Admin calls `updateRSETHPrice()`. `_getTotalEthInProtocol()` now uses the corrected price `1.00e18`, so `totalETHInProtocol` is lower. `rsETHPrice` drops.
5. All pre-existing rsETH holders now hold shares backed by less ETH — their yield has been stolen by the attacker's over-minted rsETH. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-36)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L336-344)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

```

**File:** contracts/LRTWithdrawalManager.sol (L590-594)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
    }
```
