Audit Report

## Title
Missing Chainlink Oracle Data Validation Allows Stale Prices to Corrupt rsETH Exchange Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice` calls `latestRoundData()` but silently discards `updatedAt`, `roundId`, and `answeredInRound`, accepting stale, zero, or negative prices without any integrity check. A stale price propagates through `LRTOracle._updateRsETHPrice()` and corrupts the `rsETHPrice` used to determine how much rsETH is minted per deposited ETH/LST, enabling depositors to extract excess rsETH at the expense of existing holders.

## Finding Description

`ChainlinkPriceOracle.getAssetPrice` (lines 49–55) discards every return value from `latestRoundData()` except `price`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

Three validations are absent:
1. **No staleness check** — `updatedAt` is never compared to `block.timestamp`. A feed that has not been updated for hours is accepted as current.
2. **No positive-price check** — `int256 price` is cast directly to `uint256`. A zero price returns `0`; a negative price wraps to near-`type(uint256).max` and causes arithmetic overflow (revert) at the multiplication.
3. **No `answeredInRound >= roundId` check** — round completeness is never verified.

The stale price flows through `LRTOracle.getAssetPrice` → `_getTotalEthInProtocol` → `_updateRsETHPrice`, which sets `rsETHPrice`. `updateRSETHPrice()` is public and permissionless (line 87), so any caller can trigger a price update at any time, including during a known stale window.

The protocol does have a `pricePercentageLimit` downside guard (lines 270–282 of `LRTOracle.sol`): if `newRsETHPrice` drops more than `pricePercentageLimit` below `highestRsethPrice`, the protocol pauses. However, this guard is **insufficient** for three reasons:
- If `pricePercentageLimit == 0` (its default unset value), the guard is entirely disabled.
- If the stale price deviation is smaller than the configured limit (e.g., a 2% stale deviation with a 5% limit), the bad price is accepted and `rsETHPrice` is updated to the stale value without any pause.
- The guard compares against `highestRsethPrice` (all-time high), not the previous price, so a feed that has been slowly drifting stale over many updates may never trigger it.

## Impact Explanation

**Stale price (positive, within `pricePercentageLimit` threshold):** `_getTotalEthInProtocol` underestimates total ETH backing rsETH. `newRsETHPrice` is set below its true value. Any subsequent deposit (via `LRTDepositPool` on mainnet, or via `RSETHPoolV3` on L2 after the rate propagates cross-chain) mints more rsETH than the depositor is entitled to, diluting existing holders. This constitutes **theft of unclaimed yield** (High).

**Zero price:** The affected asset's entire TVL contribution is zeroed in `_getTotalEthInProtocol`, severely depressing `rsETHPrice` and enabling the same over-minting. Depending on the magnitude, this may also trigger the downside pause.

**Negative price:** `uint256(negative_int256)` wraps to a huge value; the subsequent `* 1e18` multiplication overflows and reverts in Solidity 0.8.x. `updateRSETHPrice()` becomes permanently reverting until the feed recovers — **temporary freeze of the price-update mechanism** (Medium).

## Likelihood Explanation

Chainlink LST/ETH feeds (stETH/ETH, rETH/ETH, etc.) have heartbeat intervals of 24 hours and deviate-by-0.5% triggers. During network congestion or sequencer downtime, feeds can go stale within their heartbeat window while still returning a price that is within the `pricePercentageLimit` threshold. `updateRSETHPrice()` is public, so an attacker can deliberately time the call to coincide with a known stale window. The stale price scenario is realistic and repeatable. Likelihood: **Medium**.

## Recommendation

Add staleness and validity guards inside `getAssetPrice`. Store per-feed staleness thresholds in a mapping since heartbeat intervals differ across feeds:

```solidity
mapping(address asset => uint256 maxStaleness) public assetMaxStaleness;

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound)
        = priceFeed.latestRoundData();

    require(price > 0, "ChainlinkPriceOracle: non-positive price");
    uint256 maxStaleness = assetMaxStaleness[asset];
    require(
        maxStaleness == 0 || (updatedAt != 0 && block.timestamp - updatedAt <= maxStaleness),
        "ChainlinkPriceOracle: stale price"
    );
    require(answeredInRound >= roundId, "ChainlinkPriceOracle: incomplete round");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

## Proof of Concept

1. stETH/ETH Chainlink feed heartbeat is 24 h; last update was 23 h 50 min ago. Stale price: 0.97e18 (actual: 1.00e18). `pricePercentageLimit` is set to 5e16 (5%), so a 3% drop does not trigger the pause.
2. Attacker calls `LRTOracle.updateRSETHPrice()` (public, no role required).
3. `ChainlinkPriceOracle.getAssetPrice(stETH)` returns `0.97e18` — no staleness check fires.
4. `_getTotalEthInProtocol()` underestimates total ETH by ~3% of the stETH TVL.
5. `newRsETHPrice` is set ~3% below its true value; the downside guard does not trigger (3% < 5% limit).
6. `rsETHPrice` is written to storage at the depressed value.
7. Attacker calls `LRTDepositPool.depositAsset(stETH, amount, ...)`. The deposit pool reads `LRTOracle.rsETHPrice()` to compute rsETH to mint, issuing ~3% excess rsETH to the attacker.
8. Attacker holds the excess rsETH; when the feed recovers and `rsETHPrice` is corrected upward, the attacker's rsETH is worth more than they paid, extracting value from existing holders.

**Foundry fork test outline:**
```solidity
function testStaleChainlinkPriceCorruptsRsETHRate() public {
    // Fork mainnet at a block where stETH/ETH feed is near its heartbeat boundary
    // Mock latestRoundData to return a price with updatedAt = block.timestamp - 23.9 hours
    // Call LRTOracle.updateRSETHPrice()
    // Assert rsETHPrice < true price
    // Deposit stETH and assert rsETH minted > fair amount
}
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** contracts/LRTOracle.sol (L249-250)
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

**File:** contracts/LRTOracle.sol (L331-343)
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
```
