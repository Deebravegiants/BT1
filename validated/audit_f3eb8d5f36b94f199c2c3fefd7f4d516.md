Audit Report

## Title
Chainlink Oracle Return Values Not Validated in `ChainlinkPriceOracle.getAssetPrice()`, Enabling Incorrect rsETH Price Computation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `price`, with no validation for a stale round (`answeredInRound < roundId`), an incomplete round (`updatedAt == 0`), or a zero/negative answer. The unvalidated price propagates through `LRTOracle._updateRsETHPrice()` into the global `rsETHPrice`, which governs all deposit and withdrawal accounting. The same repository's `ChainlinkOracleForRSETHPoolCollateral.getRate()` already applies all three checks, confirming developer awareness of the pattern.

## Finding Description
In `contracts/oracles/ChainlinkPriceOracle.sol` at L52–54, `getAssetPrice()` silently discards `roundId`, `startedAt`, `updatedAt`, and `answeredInRound`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` validates all three conditions:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

The unvalidated price propagates as follows:

1. `ChainlinkPriceOracle.getAssetPrice()` is called by `LRTOracle.getAssetPrice()` at L157. [3](#0-2) 
2. `LRTOracle.getAssetPrice()` is called inside `_getTotalEthInProtocol()` at L339, which accumulates `assetER * totalAssetAmt` for every supported asset. [4](#0-3) 
3. `_getTotalEthInProtocol()` feeds `_updateRsETHPrice()`, which computes and stores the global `rsETHPrice` at L250 and L313. [5](#0-4) 
4. `updateRSETHPrice()` is public with no access control beyond `whenNotPaused`, callable by any address. [6](#0-5) 

**Stale round (`answeredInRound < roundId`):** A stale price materially below the true price deflates `totalETHInProtocol`, producing a deflated `rsETHPrice`. Any depositor who calls `updateRSETHPrice()` immediately before depositing receives more rsETH than their assets are worth, diluting all existing rsETH holders.

**Zero price:** `assetER = 0` excludes the affected asset's entire TVL from `totalETHInProtocol`, artificially deflating `rsETHPrice`. If the deflation exceeds `pricePercentageLimit`, the protocol auto-pauses (temporary freeze). If `pricePercentageLimit == 0`, `rsETHPrice` is silently set to a deflated value.

**Negative price:** `uint256(negative_int256)` wraps to a value near `2^256`. The subsequent multiplication `uint256(price) * 1e18` overflows and reverts in Solidity 0.8.x (checked arithmetic), causing `updateRSETHPrice()` to revert — a temporary DoS rather than insolvency. The insolvency claim for negative prices is overstated.

The existing `pricePercentageLimit` downside guard at L270–282 only mitigates stale-price scenarios where the deviation exceeds the configured threshold; it provides no protection when `pricePercentageLimit == 0` or when the stale price is within the threshold. [7](#0-6) 

## Impact Explanation
**Primary — High: Theft of unclaimed yield.** A stale Chainlink price that is materially lower than the true price deflates `rsETHPrice`. An attacker who triggers `updateRSETHPrice()` at that moment and immediately deposits receives more rsETH than their deposit is worth at the true price. When the feed recovers and `rsETHPrice` is corrected, the attacker's rsETH is worth more than they paid, at the direct expense of all existing rsETH holders' accrued yield.

**Secondary — Medium: Temporary freezing of funds.** A zero price for any supported asset deflates `rsETHPrice` enough to trigger the downside-protection auto-pause (if `pricePercentageLimit > 0`), freezing all deposits and withdrawals until an admin unpauses.

## Likelihood Explanation
Chainlink feeds can return stale data during network congestion, sequencer downtime, or when neither the deviation threshold nor the heartbeat has been met. The `updateRSETHPrice()` function is fully permissionless — any EOA or contract can call it at any time. An attacker can monitor Chainlink round data on-chain, detect a stale round, and atomically call `updateRSETHPrice()` followed by a deposit in the same block. No privileged access, no victim mistake, and no external protocol compromise is required.

## Recommendation
Apply the same validation pattern already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, consider adding a maximum staleness threshold (e.g., `block.timestamp - updatedAt > MAX_STALENESS`) calibrated to each feed's heartbeat interval.

## Proof of Concept
1. A Chainlink LST/ETH feed enters a stale round (`answeredInRound < roundId`) due to network congestion, returning a price 3% below the true market price.
2. An attacker observes the stale round on-chain (all Chainlink round data is public).
3. The attacker calls `LRTOracle.updateRSETHPrice()` (public, no access control). The call chain is: `updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `LRTOracle.getAssetPrice()` → `ChainlinkPriceOracle.getAssetPrice()` → `latestRoundData()` returns stale price without revert.
4. `rsETHPrice` is stored 3% below its true value (assuming the deviation is within `pricePercentageLimit` or `pricePercentageLimit == 0`).
5. The attacker immediately deposits assets via `LRTDepositPool`, receiving ~3% more rsETH than their deposit is worth at the true price.
6. When the Chainlink feed recovers and `rsETHPrice` is updated to the correct value, the attacker's rsETH is worth 3% more than they paid, at the expense of all existing rsETH holders' accrued yield.

**Foundry fork test plan:** Fork mainnet at a block where a Chainlink feed has `answeredInRound < roundId`. Deploy or point to the existing `ChainlinkPriceOracle`. Call `updateRSETHPrice()` as an unprivileged address. Assert that `rsETHPrice` is set to the stale deflated value. Then deposit as the attacker, record rsETH received. Advance the block to a recovered round, call `updateRSETHPrice()` again, and assert the attacker's rsETH balance is worth more ETH than deposited, while an existing holder's share is diluted.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L249-251)
```text
        // compute new rsETH price based on total ETH minus fee
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
