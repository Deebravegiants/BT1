### Title
Missing Chainlink Price Feed Staleness Check Enables Inflated rsETH Minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards the `updatedAt` timestamp, performing no staleness check. A stale (expired) price is accepted as valid, directly analogous to the reference finding where expired license terms were accepted without validation. Because this oracle feeds the rsETH minting calculation in `LRTDepositPool`, an attacker can exploit a stale price during an LST depeg event to mint rsETH at an inflated rate, stealing value from existing rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the latest price from a Chainlink aggregator:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The `updatedAt` field — which indicates when the price was last refreshed — is completely discarded via the blank tuple slots. No maximum age threshold (e.g., `block.timestamp - updatedAt > MAX_STALENESS`) is enforced.

This price is consumed by `LRTDepositPool.getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

which is called unconditionally inside `_beforeDeposit()`, which is called by both `depositETH()` and `depositAsset()`.

---

### Impact Explanation

If a supported LST (e.g., stETH, rETH) depegs from ETH while the Chainlink feed is stale (heartbeat not yet triggered, oracle nodes lagging, or network congestion), the protocol continues to price the LST at its pre-depeg value. An attacker deposits the depegged LST at the stale inflated price and receives more rsETH than the deposited assets are worth. When the oracle eventually updates, the rsETH price drops, diluting all existing holders. This constitutes **theft of yield / protocol insolvency** — existing rsETH holders bear the loss of the over-minted supply.

Impact: **High** — theft of unclaimed yield / protocol insolvency from existing rsETH holders.

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 1 hour for ETH/stETH). During periods of high network congestion, oracle node downtime, or rapid price movement that has not yet crossed the deviation threshold, feeds can remain stale for minutes to hours. LST depeg events (e.g., stETH during the Merge, USDC depeg) are historically correlated with exactly these conditions. An attacker monitoring mempool and oracle state can time the exploit precisely.

Likelihood: **Medium** — requires a stale feed window coinciding with a depeg, but both conditions are historically observed and the attacker has no special privileges.

---

### Recommendation

Add a configurable `maxStaleness` parameter and validate `updatedAt` in `getAssetPrice()`:

```solidity
(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
if (block.timestamp - updatedAt > maxStaleness) {
    revert StalePriceFeed(asset, updatedAt);
}
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

Also validate that `price > 0` to guard against a zero/negative answer.

---

### Proof of Concept

1. Chainlink stETH/ETH feed has a 1-hour heartbeat. At `T=0`, the feed reports `1.0 ETH` per stETH (`updatedAt = T`).
2. At `T+30min`, stETH depegs to `0.95 ETH` due to a slashing event. The Chainlink feed has not yet updated (heartbeat not triggered, deviation threshold not crossed).
3. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
4. `ChainlinkPriceOracle.getAssetPrice(stETH)` returns the stale `1.0 ETH` price.
5. `getRsETHAmountToMint` mints rsETH as if 1000 stETH = 1000 ETH worth of rsETH.
6. Actual value deposited is only 950 ETH. The 50 ETH difference is extracted from existing rsETH holders when the oracle updates and rsETH price adjusts downward.

The root cause — discarding `updatedAt` — is at: [1](#0-0) 

The stale price propagates through: [2](#0-1) 

via the deposit entry points: [3](#0-2)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-52)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();
```

**File:** contracts/LRTDepositPool.sol (L99-117)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
