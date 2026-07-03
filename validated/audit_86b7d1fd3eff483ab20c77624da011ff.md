Audit Report

## Title
Missing Staleness and Validity Checks in `ChainlinkPriceOracle::getAssetPrice` Enables Permissionless Protocol Pause and Yield Theft via Deflated rsETH Price - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards `updatedAt`, `answeredInRound`, and performs no positivity check on `price`. A zero or stale price silently propagates into `LRTOracle._getTotalEthInProtocol()`, collapsing the computed TVL and driving `rsETHPrice` to an artificially low value. Because `updateRSETHPrice()` is a public, permissionless function, any external caller can trigger this during any Chainlink feed outage, causing either a forced protocol pause (temporary fund freeze) or, when the price drop falls within the configured limit, an exploitable deflated rsETH price that allows over-minting of rsETH at the expense of existing holders.

## Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price with no defensive checks:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();   // updatedAt, answeredInRound discarded
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Three fields returned by `latestRoundData` are silently discarded: `updatedAt` (staleness), `answeredInRound` (round completeness), and `price` is not checked to be `> 0`. When `answeredInRound < roundId` (incomplete round) or `updatedAt` is beyond the heartbeat threshold, `price` may be `0`, causing `getAssetPrice` to return `0`.

This zero flows into `_getTotalEthInProtocol()`:

```solidity
// contracts/LRTOracle.sol L339-343
uint256 assetER = getAssetPrice(asset);          // returns 0 on stale/incomplete round
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);  // contributes 0 for this asset
```

And then into `_updateRsETHPrice()`:

```solidity
// contracts/LRTOracle.sol L250
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

With one asset's ETH value zeroed, `newRsETHPrice` drops sharply. The downside-protection logic then evaluates:

```solidity
// contracts/LRTOracle.sol L270-282
if (newRsETHPrice < highestRsethPrice) {
    uint256 diff = highestRsethPrice - newRsETHPrice;
    bool isPriceDecreaseOffLimit =
        pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
    if (isPriceDecreaseOffLimit) {
        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!withdrawalManager.paused()) withdrawalManager.pause();
        _pause();
        return;   // rsETHPrice NOT updated; protocol frozen
    }
}
// ...
rsETHPrice = newRsETHPrice;  // L313: written at deflated value if drop is within limit
```

**Path A (pause):** If `pricePercentageLimit > 0` and the drop exceeds the limit, the protocol pauses and returns early without updating `rsETHPrice`. All deposits and withdrawals are frozen until admin unpauses.

**Path B (yield theft):** If `pricePercentageLimit = 0` or the stale asset is a small enough fraction of TVL that the drop falls within the limit, `rsETHPrice` is written at the deflated value (L313). An attacker who then calls `depositAsset()` with a healthy asset receives rsETH computed as:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

With `rsETHPrice` deflated, the denominator is smaller, so the attacker receives more rsETH per unit of deposited LST than the true exchange rate warrants, diluting all existing rsETH holders.

The trigger function is fully permissionless:

```solidity
// contracts/LRTOracle.sol L87
function updateRSETHPrice() public whenNotPaused {
```

No existing guard prevents an unprivileged caller from invoking this during a Chainlink feed outage.

## Impact Explanation

**Path A — Temporary Freezing of Funds (Medium):** Any external caller can invoke `updateRSETHPrice()` while a Chainlink feed is stale or in an incomplete round. If `pricePercentageLimit` is configured (as stated to be the case in production), the artificial price drop triggers `lrtDepositPool.pause()`, `withdrawalManager.pause()`, and `_pause()` on `LRTOracle`. All user deposits and withdrawals are frozen until an admin manually unpauses. This matches the allowed impact: *Temporary freezing of funds*.

**Path B — Theft of Unclaimed Yield (High):** When the price drop falls within the configured limit (e.g., the stale asset is a minor fraction of TVL), `rsETHPrice` is committed at the deflated value. An attacker immediately deposits a healthy LST asset and receives rsETH at the deflated price. When the oracle recovers and `rsETHPrice` normalizes, the attacker's rsETH is worth more than they paid, extracting value from all existing holders. This matches the allowed impact: *Theft of unclaimed yield*.

## Likelihood Explanation

Chainlink feeds experience staleness during network congestion, sequencer downtime (on L2), or at the boundary of the heartbeat interval. The `answeredInRound < roundId` condition occurs naturally during any round that has not yet been answered. `updateRSETHPrice()` is public and callable by any EOA or contract, including bots that monitor oracle health. No privileged access, governance action, or oracle operator compromise is required. The exploitability window equals the full duration of any oracle outage. This is a realistic, externally-triggerable condition.

## Recommendation

Add staleness, round-completeness, and positivity checks to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
uint48 constant STALENESS_THRESHOLD = 1 hours; // tune per feed heartbeat

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > STALENESS_THRESHOLD) revert StalePrice();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, `_updateRsETHPrice()` should revert rather than silently proceed if any oracle call returns an invalid price, preventing corrupted price updates from being committed to state.

## Proof of Concept

**Path A (Temporary Freeze):**
1. Chainlink's stETH/ETH feed enters an incomplete round (`answeredInRound < roundId`), causing `latestRoundData()` to return `price = 0`.
2. Attacker calls `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_getTotalEthInProtocol()` calls `getAssetPrice(stETH)` → `ChainlinkPriceOracle` returns `0`.
4. stETH's contribution to `totalETHInProtocol` is zeroed. If stETH represents 40% of TVL, `totalETHInProtocol` drops by 40%.
5. `newRsETHPrice = (0.6 * previousTVL) / rsethSupply` — a 40% drop.
6. With `pricePercentageLimit = 5e16` (5%): `diff > 0.05 * highestRsethPrice` → true → `lrtDepositPool.pause()`, `withdrawalManager.pause()`, `_pause()` called.
7. All user deposits and withdrawals are frozen until admin intervention.

**Path B (Yield Theft):**
1. A minor supported asset (e.g., 3% of TVL) has its Chainlink feed return `price = 0`.
2. Attacker calls `updateRSETHPrice()` → `rsETHPrice` drops by ~3%, within the `pricePercentageLimit` → price is written at deflated value (L313).
3. Attacker immediately calls `depositAsset(healthyLST, largeAmount, 0, "")` → receives rsETH computed with the deflated `rsETHPrice` denominator → over-minted rsETH.
4. Oracle recovers; next legitimate `updateRSETHPrice()` call restores `rsETHPrice` to true value.
5. Attacker's rsETH is now worth more than deposited, extracting yield from all existing holders. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
            }
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
