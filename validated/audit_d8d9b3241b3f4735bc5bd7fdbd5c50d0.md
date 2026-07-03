Audit Report

## Title
Missing Chainlink Price Staleness Check in `ChainlinkPriceOracle.getAssetPrice()` Enables Stale-Price-Triggered Protocol Pause - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `price`, accepting stale or incomplete round data without validation. A stale lower price propagates into `LRTOracle._updateRsETHPrice()`, which can trigger an automatic protocol-wide pause freezing all user deposits and withdrawals. The same contract codebase already applies the missing checks in `ChainlinkOracleForRSETHPoolCollateral`, confirming the protocol's awareness of the requirement.

## Finding Description

`ChainlinkPriceOracle.getAssetPrice()` (L52) silently discards `updatedAt` and `answeredInRound`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The stale price flows through `LRTOracle.getAssetPrice()` → `_getTotalEthInProtocol()` (L339) → `_updateRsETHPrice()` (L250), where `newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply)`. If the stale price is lower than the true price, `totalETHInProtocol` is underestimated and `newRsETHPrice` falls. At L270–281, if the drop exceeds `pricePercentageLimit` relative to `highestRsethPrice`, the contract calls `lrtDepositPool.pause()`, `withdrawalManager.pause()`, and `_pause()`, freezing all deposits and withdrawals.

`updateRSETHPrice()` (L87) is `public whenNotPaused` — any unprivileged caller can invoke it at any moment a feed is stale. The existing guard at L273 (`pricePercentageLimit > 0 && diff > ...`) only prevents the pause when `pricePercentageLimit` is zero; when it is set to any non-zero value, a sufficiently stale price triggers the freeze.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` (L30–32) explicitly checks `answeredInRound < roundID` and `timestamp == 0` before returning a price, demonstrating the protocol's own standard for safe Chainlink consumption.

## Impact Explanation

**Medium — Temporary freezing of funds.** An unprivileged attacker can call `updateRSETHPrice()` at any moment a Chainlink LST/ETH feed is stale. If the stale price is sufficiently lower than the true price, the auto-pause at L277–281 freezes `LRTDepositPool` and `LRTWithdrawalManager`, blocking all user deposits and withdrawals until an admin manually unpauses. This is a concrete, reachable impact within the allowed scope.

**Low — Contract fails to deliver promised returns.** If a stale higher price is accepted, `rsETHPrice` is inflated. Depositors calling `getRsETHAmountToMint()` receive fewer rsETH tokens than entitled, since `rsethAmountToMint = (amount * assetPrice) / rsETHPrice` — a higher denominator reduces the mint amount.

## Likelihood Explanation

`updateRSETHPrice()` is permissionless. Chainlink feeds go stale during L2 sequencer downtime, network congestion, or feed deprecation — all real-world events. The protocol is deployed on multiple chains, increasing exposure. No special privileges or victim cooperation are required; the attacker only needs to observe a stale feed and call the public function. The condition is repeatable whenever a feed lags.

## Recommendation

Apply the same staleness checks already present in `ChainlinkOracleForRSETHPoolCollateral.sol` to `ChainlinkPriceOracle.getAssetPrice()`:

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

Additionally, consider adding a configurable heartbeat check (`block.timestamp - updatedAt > maxStaleness`) per feed to guard against prices that are non-zero but outdated beyond the feed's expected update interval.

## Proof of Concept

1. Deploy or fork with a Chainlink LST/ETH feed (e.g., stETH/ETH) whose `updatedAt` is stale and `answer` is lower than the current true price.
2. Ensure `pricePercentageLimit` is set to a non-zero value (e.g., 1e16 for 1%) and `highestRsethPrice` reflects the true price.
3. Call `LRTOracle.updateRSETHPrice()` from any EOA.
4. Observe: `_getTotalEthInProtocol()` returns a lower-than-true value; `newRsETHPrice` falls below `highestRsethPrice` by more than `pricePercentageLimit`.
5. Observe: `lrtDepositPool.paused() == true`, `withdrawalManager.paused() == true`, `LRTOracle.paused == true`.
6. All user deposits and withdrawals are frozen; only an admin can unpause.

**Foundry fork test outline:**
```solidity
function testStaleOraclePausesProtocol() public {
    // mock latestRoundData to return stale lower price
    vm.mockCall(priceFeed, abi.encodeWithSelector(AggregatorV3Interface.latestRoundData.selector),
        abi.encode(uint80(10), int256(staleLowerPrice), uint256(0), uint256(block.timestamp - 2 hours), uint80(9)));
    // call as unprivileged user
    vm.prank(attacker);
    lrtOracle.updateRSETHPrice();
    assertTrue(lrtDepositPool.paused());
    assertTrue(withdrawalManager.paused());
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
