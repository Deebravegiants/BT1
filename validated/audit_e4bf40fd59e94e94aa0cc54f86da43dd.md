Audit Report

## Title
Missing Chainlink Staleness Validation in `getAssetPrice` Enables rsETH Over-Minting via Deflated `rsETHPrice` - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` discards all `latestRoundData()` return values except `answer`, performing no heartbeat, round-completeness, or non-zero price check. Because `updateRSETHPrice()` is callable by any unprivileged address and the stored `rsETHPrice` is the denominator in the rsETH minting formula, a natural Chainlink staleness event on any one supported LST feed allows an attacker to mint rsETH at a deflated price, directly diluting every existing rsETH holder's proportional ETH claim.

## Finding Description

**Root cause — no staleness validation in `ChainlinkPriceOracle.getAssetPrice()`:**

`contracts/oracles/ChainlinkPriceOracle.sol` L52 binds only the second return slot of `latestRoundData()`; `updatedAt` and `answeredInRound` are silently discarded:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

**Price propagation path:**

`LRTOracle._getTotalEthInProtocol()` sums `assetAmount × assetPrice` for every supported LST using the unchecked oracle: [2](#0-1) 

That total feeds `_updateRsETHPrice()`, which writes `rsETHPrice` to storage. The entry point is unrestricted — any address may call it: [3](#0-2) 

**Minting formula uses stored `rsETHPrice` as denominator:**

`LRTDepositPool.getRsETHAmountToMint()` divides by the stored (potentially deflated) `rsETHPrice`: [4](#0-3) 

**Exploit flow:**

1. A Chainlink feed for one supported LST (e.g. stETH/ETH) goes stale with a price below the true market value.
2. Attacker calls `updateRSETHPrice()` (public, no role). `_getTotalEthInProtocol()` uses the stale-low price, deflating `totalETHInProtocol` and therefore `rsETHPrice`.
3. The partial downside-protection guard (`pricePercentageLimit`) only auto-pauses for deviations exceeding the configured threshold. If `pricePercentageLimit == 0` (unset), the guard is entirely bypassed: [5](#0-4) 
4. Attacker calls `depositAsset(cbETH, ...)`. The numerator `lrtOracle.getAssetPrice(cbETH)` is a live call returning the correct cbETH price; the denominator `lrtOracle.rsETHPrice()` is the deflated stored value. The attacker receives excess rsETH proportional to the deflation.
5. When the stale feed recovers and `rsETHPrice` is updated back to its true value, the attacker's excess rsETH is worth more ETH than deposited — at the expense of all prior holders.

**Contrast with `ChainlinkOracleForRSETHPoolCollateral`**, which already performs the missing checks, confirming the team is aware of the pattern: [6](#0-5) 

## Impact Explanation

Existing rsETH holders suffer dilution: their proportional claim on the underlying ETH pool shrinks without compensation. This is direct, at-rest fund loss for every holder at the time of the exploit, matching **Critical — direct theft of user funds**. Magnitude scales with the stale asset's TVL share and the degree of price deviation before feed recovery.

## Likelihood Explanation

Chainlink feeds have historically gone stale during network congestion or node operator issues. The protocol supports multiple LST assets, each with its own feed, increasing the probability that at least one feed lags. The attacker requires no special role, no front-running, and no oracle manipulation — only the ability to observe on-chain that a feed's `updatedAt` is old and to call two public functions (`updateRSETHPrice` then `depositAsset`). **Likelihood: Low-to-Medium.**

## Recommendation

1. **Add staleness and round-completeness checks in `ChainlinkPriceOracle.getAssetPrice()`**, mirroring `ChainlinkOracleForRSETHPoolCollateral` and adding a configurable heartbeat window:

```solidity
(uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound)
    = priceFeed.latestRoundData();

require(answeredInRound >= roundId,                        "Stale: incomplete round");
require(updatedAt != 0,                                    "Stale: round not complete");
require(block.timestamp - updatedAt <= maxStaleness[asset],"Stale: heartbeat exceeded");
require(price > 0,                                         "Invalid price");
```

2. **Store a per-feed `maxStaleness` value** (e.g. 3600 s for a 1-hour heartbeat feed) set by the LRT manager alongside `updatePriceFeedFor`.

3. **Apply the same fix to `RSETHPriceFeed.latestRoundData()`**, which forwards the raw ETH/USD answer without any staleness validation: [7](#0-6) 

## Proof of Concept

**Setup:** Protocol holds 1 000 stETH (stETH/ETH feed = 0.999 stale, real = 1.001) and 1 000 cbETH (cbETH/ETH feed = 1.05, live). rsETH supply = 2 049 rsETH. Real `rsETHPrice` ≈ 1.001 ETH.

**Step 1 — Feed goes stale.** stETH/ETH Chainlink feed stops updating; last reported price = 0.999.

**Step 2 — Attacker calls `updateRSETHPrice()` (public, no role).**
- `_getTotalEthInProtocol()` = `1000 × 0.999 + 1000 × 1.05` = 2049 ETH (stale).
- Real total = `1000 × 1.001 + 1000 × 1.05` = 2051 ETH.
- `rsETHPrice` written as `2049 / 2049 = 1.000 ETH` instead of real `≈ 1.001 ETH`.

**Step 3 — Attacker calls `depositAsset(cbETH, 100e18, ...)`.**
- `rsethAmountToMint = (100 × 1.05) / 1.000 = 105 rsETH`
- Correct: `(100 × 1.05) / 1.001 ≈ 104.9 rsETH`
- Attacker receives ~0.1 rsETH excess per 100 cbETH deposited.

**Step 4 — Feed recovers.** `updateRSETHPrice()` restores `rsETHPrice ≈ 1.001`. Attacker's 105 rsETH is now worth more ETH than deposited, at the expense of all prior holders.

**Foundry fork test plan:**
1. Fork mainnet; deploy/configure protocol with stETH and cbETH feeds.
2. Mock the stETH/ETH aggregator to return a stale `updatedAt` (e.g. `block.timestamp - 2 hours`) with a slightly lower price.
3. Call `lrtOracle.updateRSETHPrice()` as an unprivileged EOA.
4. Assert `rsETHPrice` is lower than the value computed with the correct price.
5. Call `depositPool.depositAsset(cbETH, 100e18, 0, "")` as the attacker.
6. Assert attacker received more rsETH than `(100e18 × P_cbETH) / rsETHPrice_correct`.
7. Mock the aggregator to return the correct price; call `updateRSETHPrice()` again.
8. Assert attacker's rsETH balance represents more ETH than deposited, confirming dilution of prior holders.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L273-281)
```text
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L27-33)
```text
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

```

**File:** contracts/oracles/RSETHPriceFeed.sol (L63-70)
```text
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound)
    {
        (roundId, answer, startedAt, updatedAt, answeredInRound) = ETH_TO_USD.latestRoundData();
        answer = int256(RS_ETH_ORACLE.rsETHPrice()) * answer / 1e18;
    }
```
