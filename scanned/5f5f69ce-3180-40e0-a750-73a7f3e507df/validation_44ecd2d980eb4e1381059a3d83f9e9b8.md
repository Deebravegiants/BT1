### Title
Missing Chainlink Price Staleness Check Allows Stale LST Prices to Corrupt rsETH Exchange Rate and Trigger Illegitimate Fee Minting — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but silently discards the `updatedAt` timestamp and `answeredInRound` return values. There is no check that the price is recent. This is the direct analog of H-02: just as the Anchor feeder accepted delayed transactions with stale prices because `last_updated_time` was always set to `block.time`, this contract accepts a stale Chainlink answer as if it were current. The stale price propagates into `LRTOracle._getTotalEthInProtocol()`, corrupts the rsETH exchange rate, and can trigger illegitimate protocol fee minting that dilutes existing rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` is the price source for every supported LST asset (stETH, rETH, ETHx, swETH, sfrxETH, etc.) in the protocol:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-L55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`latestRoundData()` returns five values: `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The code destructures only `price` (the second slot); `updatedAt` and `answeredInRound` are thrown away. No maximum age check is applied to `updatedAt`, and no `answeredInRound < roundId` check is applied.

Contrast this with `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same repository, which correctly validates all three conditions:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L27-L32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The stale price returned by `ChainlinkPriceOracle.getAssetPrice()` is consumed by `LRTOracle.getAssetPrice()`, which is called inside `_getTotalEthInProtocol()`:

```solidity
// contracts/LRTOracle.sol L336-L343
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    ...
}
```

`_getTotalEthInProtocol()` feeds directly into `_updateRsETHPrice()`, which computes the new rsETH price and decides whether to mint protocol fees:

```solidity
// contracts/LRTOracle.sol L244-L250
if (!protocolPaused && totalETHInProtocol > previousTVL) {
    uint256 rewardAmount = totalETHInProtocol - previousTVL;
    protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
}
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

`updateRSETHPrice()` is a **public, permissionless function** — any external caller can trigger it:

```solidity
// contracts/LRTOracle.sol L87-L89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

---

### Impact Explanation

When a Chainlink feed for a supported LST goes stale at an inflated price:

1. `totalETHInProtocol` is overstated.
2. `totalETHInProtocol > previousTVL` evaluates to `true` even though no real yield was earned.
3. A protocol fee is minted in rsETH to the treasury (`IRSETH.mint(treasury, rsethAmountToMintAsProtocolFee)`).
4. This dilutes all existing rsETH holders — their share of the underlying pool shrinks without any corresponding yield having been generated.
5. When the feed recovers, `newRsETHPrice` drops back, but the fee tokens already minted to the treasury are not burned.

This constitutes **theft of unclaimed yield** from existing rsETH holders, transferred to the protocol treasury. The magnitude scales with the size of the stale price deviation and the total TVL of the affected asset.

Additionally, a stale low price causes `newRsETHPrice` to be understated, allowing a depositor to mint rsETH at a discount — **temporary theft of funds** from existing holders.

**Impact: High** — Theft of unclaimed yield / temporary theft of funds from rsETH holders.

---

### Likelihood Explanation

Chainlink feeds are known to go stale during:
- Ethereum network congestion (high gas prices preventing oracle updates)
- Chainlink node outages or degraded performance
- Circuit-breaker events where the feed pauses at a boundary price

These are realistic, documented scenarios. The attack requires no privileged access: any external account can call `updateRSETHPrice()` at the moment a feed is stale to lock in the corrupted price and trigger fee minting.

**Likelihood: Medium** — Requires a Chainlink feed to be stale, which is a known and periodic occurrence, combined with a public permissionless trigger.

---

### Recommendation

Apply the same staleness checks already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    if (block.timestamp - updatedAt > MAX_PRICE_AGE) revert StalePrice(); // e.g. 24 hours

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

A configurable `MAX_PRICE_AGE` per asset (matching each feed's heartbeat) is recommended.

---

### Proof of Concept

**Setup:**
- stETH is a supported asset with a large TVL (e.g., 10,000 stETH ≈ 10,000 ETH at 1:1)
- Chainlink stETH/ETH feed last updated 26 hours ago at `1.05e18` (stale high price)
- True current stETH/ETH rate is `1.00e18`
- `rsETHPrice` = `1.00e18`, `rsethSupply` = 10,000 rsETH, `previousTVL` = 10,000 ETH

**Attack steps:**
1. Chainlink stETH/ETH feed goes stale at `1.05e18` due to network congestion.
2. Attacker calls `LRTOracle.updateRSETHPrice()`.
3. `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns `1.05e18` (stale).
4. `totalETHInProtocol` = 10,000 × 1.05 = 10,500 ETH.
5. `previousTVL` = 10,000 × 1.00 = 10,000 ETH.
6. `rewardAmount` = 500 ETH → `protocolFeeInETH` = 500 × fee% (e.g., 10% = 50 ETH).
7. `newRsETHPrice` = (10,500 − 50) / 10,000 = `1.045e18`.
8. `rsethAmountToMintAsProtocolFee` = 50 / 1.045 ≈ 47.8 rsETH minted to treasury.
9. Feed recovers; next honest `updateRSETHPrice()` call computes `totalETHInProtocol` = 10,000 ETH with 10,047.8 rsETH supply → `rsETHPrice` drops to ≈ `0.9952e18`.
10. All existing rsETH holders have been diluted by ~47.8 rsETH worth of value, transferred to the treasury. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTOracle.sol (L244-250)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L299-308)
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
```

**File:** contracts/LRTOracle.sol (L336-348)
```text
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
```
