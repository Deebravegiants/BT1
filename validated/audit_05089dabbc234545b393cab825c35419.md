### Title
No Chainlink Price Staleness Check Allows Stale Asset Prices to Corrupt rsETH Exchange Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but silently discards the `updatedAt` timestamp, accepting arbitrarily stale prices with no heartbeat or age validation. This stale price propagates through `LRTOracle._getTotalEthInProtocol()` into the publicly callable `updateRSETHPrice()`, corrupting the stored `rsETHPrice` that governs how many rsETH tokens every depositor receives.

---

### Finding Description

In `contracts/oracles/ChainlinkPriceOracle.sol` line 52, `latestRoundData()` is destructured with the `updatedAt` field discarded:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
```

No check of the form `block.timestamp - updatedAt > maxStaleness` is performed. The returned `price` is used directly.

This price is consumed by the following public call chain:

1. `LRTOracle.updateRSETHPrice()` (no access control, `whenNotPaused` only) calls `_updateRsETHPrice()`
2. `_updateRsETHPrice()` calls `_getTotalEthInProtocol()`
3. `_getTotalEthInProtocol()` iterates all supported assets and calls `getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice()` for each
4. The stale price is multiplied by `totalAssetAmt` to produce `totalETHInProtocol`
5. `newRsETHPrice = (totalETHInProtocol - protocolFeeInETH) / rsethSupply` is stored as `rsETHPrice`
6. Every subsequent `LRTDepositPool.depositAsset()` / `depositETH()` call mints rsETH using this corrupted rate

For contrast, `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol` at least checks `answeredInRound < roundID` and `timestamp == 0`, but `ChainlinkPriceOracle` has **zero** staleness protection.

---

### Impact Explanation

**Severity: High — Theft of unclaimed yield / share mis-accounting**

If a Chainlink feed for a supported LST asset (e.g., stETH/ETH) goes stale at a price **below** the true market rate:

- `totalETHInProtocol` is underestimated
- `rsETHPrice` is set artificially low
- New depositors calling `depositAsset()` receive **more rsETH** than their deposit is worth
- This dilutes the rsETH holdings of all existing holders, effectively transferring value (accrued yield) from existing holders to new depositors

If the stale price is **above** the true rate, new depositors receive fewer rsETH tokens than owed — a direct loss to the depositor.

Both directions represent incorrect rsETH minting amounts that cannot be reversed once the transaction is confirmed.

---

### Likelihood Explanation

Chainlink feeds can go stale during:
- Network congestion on Ethereum mainnet
- Chainlink node outages
- Low-volatility periods where deviation thresholds are not triggered for extended periods

`updateRSETHPrice()` is callable by anyone with no access control beyond `whenNotPaused`. An attacker or any user can trigger the price update at the exact moment a feed is stale, locking in the corrupted `rsETHPrice` before the feed recovers. The protocol supports multiple LST assets (stETH, rETH, sfrxETH, swETH, ETHx), each with its own Chainlink feed — increasing the attack surface.

---

### Recommendation

Add a configurable `maxStaleness` parameter and validate `updatedAt` in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
if (block.timestamp - updatedAt > maxStaleness) revert StalePrice();
```

A typical heartbeat for LST/ETH feeds is 24 hours; `maxStaleness` should be set slightly above the feed's documented heartbeat.

---

### Proof of Concept

**Step 1 — Stale price accepted silently:** [1](#0-0) 

The `updatedAt` return value (4th position) is never captured or validated.

**Step 2 — Stale price flows into total ETH calculation:** [2](#0-1) 

`getAssetPrice(asset)` returns the stale price; it is multiplied by `totalAssetAmt` to produce `totalETHInProtocol`.

**Step 3 — Corrupted rsETH price is stored:** [3](#0-2) 

`newRsETHPrice` is derived from the stale `totalETHInProtocol` and written to storage at line 313.

**Step 4 — Public entry point, no access control:** [4](#0-3) 

Any unprivileged caller can invoke `updateRSETHPrice()` to trigger the stale-price update.

**Step 5 — Depositors receive incorrect rsETH amounts based on corrupted price:** [5](#0-4) 

`depositETH()` (and `depositAsset()`) mint rsETH using the now-corrupted `rsETHPrice` stored in `LRTOracle`.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-251)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);

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

**File:** contracts/LRTDepositPool.sol (L76-93)
```text
    function depositETH(
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        payable
        nonReentrant
        whenNotPaused
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(LRTConstants.ETH_TOKEN, msg.value, minRSETHAmountExpected);

        // interactions
        _mintRsETH(rsethAmountToMint);

        emit ETHDeposit(msg.sender, msg.value, rsethAmountToMint, referralId);
    }
```
