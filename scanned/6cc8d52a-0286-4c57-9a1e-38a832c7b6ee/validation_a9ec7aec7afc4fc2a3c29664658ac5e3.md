### Title
Missing Chainlink Price Feed Staleness Check Allows Stale Asset Prices to Corrupt rsETH Valuation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards all freshness fields (`updatedAt`, `answeredInRound`, `roundId`). This is the direct analog to `periodSize = 0`: just as that constant stripped the TWAP of its time-averaging protection and reduced it to a spot oracle, the missing staleness check here strips the Chainlink feed of its freshness guarantee and reduces it to an unconditional spot read. The same codebase already implements the correct pattern in `ChainlinkOracleForRSETHPoolCollateral`, making the omission in `ChainlinkPriceOracle` a clear design defect rather than an intentional choice.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads only the `price` field from `latestRoundData()`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol  line 52
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The four other return values — `roundId`, `startedAt`, `updatedAt`, `answeredInRound` — are all discarded. No check is made that `answeredInRound >= roundId` (Chainlink's own staleness flag) or that `updatedAt` is within an acceptable heartbeat window.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same repository performs both checks:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol  lines 27-32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The inconsistency confirms the omission in `ChainlinkPriceOracle` is a defect.

`ChainlinkPriceOracle.getAssetPrice()` is the oracle registered for each supported LST asset (stETH, ETHx, rETH, swETH, sfrxETH). It is consumed by `LRTOracle.getAssetPrice()`, which is called inside `LRTOracle._getTotalEthInProtocol()`, which in turn drives `_updateRsETHPrice()`. The full call chain:

```
updateRSETHPrice() [public, permissionless]
  └─ _updateRsETHPrice()
       └─ _getTotalEthInProtocol()
            └─ getAssetPrice(asset)   ← ChainlinkPriceOracle, no staleness check
```

`updateRSETHPrice()` is callable by anyone (`public whenNotPaused`). An attacker can call it at any moment, including when a Chainlink feed is in a stale round, to commit a corrupted rsETH price on-chain.

---

### Impact Explanation

A stale asset price fed into `_getTotalEthInProtocol()` produces a wrong `totalETHInProtocol`, which directly sets `rsETHPrice` (line 313 of `LRTOracle.sol`). This corrupted price propagates to:

- **`LRTDepositPool.getRsETHAmountToMint()`** — users receive too many or too few rsETH tokens for their deposits.
- **`LRTWithdrawalManager._calculatePayoutAmount()`** — withdrawal amounts are computed using the wrong rsETH/ETH ratio.
- **`RSETHPriceFeed.latestRoundData()`** — the Chainlink-compatible price feed for rsETH/USD is derived from `rsETHPrice`, so downstream integrators (lending markets, DEX oracles) also receive the corrupted value.

If the stale price is lower than the true price, depositors receive excess rsETH, diluting existing holders (theft of yield / share mis-accounting). If higher, depositors are shortchanged. Either direction constitutes a contract failing to deliver promised returns; a sufficiently large deviation could cause protocol insolvency.

**Impact class**: Low (contract fails to deliver promised returns) to Medium (temporary freezing of correct pricing / theft of unclaimed yield), depending on the magnitude of the stale deviation.

---

### Likelihood Explanation

Chainlink feeds enter stale rounds during:
- Network congestion preventing oracle node transactions from landing.
- Chainlink node outages or configuration errors.
- L1 gas spikes that delay heartbeat updates.

These are not exotic conditions; they have occurred on mainnet. Because `updateRSETHPrice()` is permissionless, any actor can call it the moment a feed is stale, locking in the bad price before the feed recovers. The attacker does not need to manipulate the feed itself — they only need to time the call.

---

### Recommendation

Apply the same staleness pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    // Optional: add a per-feed heartbeat check
    // if (block.timestamp - updatedAt > MAX_HEARTBEAT) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Add a configurable `maxStaleness` per asset to handle feeds with different heartbeat intervals (e.g., 1 hour for ETH/USD vs. 24 hours for LST/ETH feeds).

---

### Proof of Concept

1. Chainlink's stETH/ETH feed enters a stale round (e.g., `answeredInRound = 99`, `roundId = 100`).
2. The feed's `latestRoundData()` still returns the last answered price from round 99, which may be significantly different from the current market price.
3. Attacker calls `LRTOracle.updateRSETHPrice()` (permissionless).
4. `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)`, which returns the stale price without reverting.
5. `rsETHPrice` is set to a wrong value on-chain.
6. Attacker (or any user) immediately calls `LRTDepositPool.depositAsset(stETH, amount)`, which calls `getRsETHAmountToMint()` using the corrupted `rsETHPrice`, receiving an incorrect rsETH amount.
7. When the Chainlink feed recovers and `rsETHPrice` is corrected, the attacker's position reflects the arbitrage gain at the expense of other rsETH holders. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

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

**File:** contracts/LRTOracle.sol (L87-88)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
```

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

```

**File:** contracts/LRTOracle.sol (L311-315)
```text
        }

        rsETHPrice = newRsETHPrice;

        emit RsETHPriceUpdate(rsETHPrice, previousPrice);
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
