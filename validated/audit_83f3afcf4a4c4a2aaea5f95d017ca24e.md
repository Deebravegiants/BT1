Audit Report

## Title
Missing Zero-Price Validation in Chainlink Oracle Enables Permissionless Auto-Pause of Deposits and Withdrawals — (`contracts/oracles/ChainlinkPriceOracle.sol`, `contracts/LRTOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice` performs no validation on the `int256 answer` returned by `latestRoundData()`, including no check that `price > 0`. If Chainlink returns `answer = 0` for any supported asset during an incomplete round, the zero propagates through `_getTotalEthInProtocol`, causing `newRsETHPrice` to be computed far below `highestRsethPrice`. Because `updateRSETHPrice()` is an unrestricted `public` function, any caller can invoke it at that moment to trigger the downside-protection auto-pause, freezing `LRTDepositPool` and `LRTWithdrawalManager` for all users.

## Finding Description

**Root cause — no zero-price guard in `ChainlinkPriceOracle.getAssetPrice`:** [1](#0-0) 

The function calls `latestRoundData()` and blindly casts the result to `uint256`. No check is made that `price > 0`, `updatedAt != 0`, or `answeredInRound >= roundId`. If Chainlink returns `answer = 0` (e.g., an in-progress round where `startedAt > 0` but `answer` has not yet been written), the function returns `0`.

**Zero price silently zeroes out that asset's TVL contribution:** [2](#0-1) 

`assetER = 0` causes `totalAssetAmt.mulWad(0) = 0`, so the entire balance of that asset is excluded from `totalETHInProtocol`.

**Undercounted TVL produces an artificially low `newRsETHPrice`:** [3](#0-2) 

With a major asset priced at 0, `newRsETHPrice` can be orders of magnitude below `highestRsethPrice`.

**Downside protection auto-pauses the protocol:** [4](#0-3) 

If `diff > pricePercentageLimit.mulWad(highestRsethPrice)`, the code calls `lrtDepositPool.pause()`, `withdrawalManager.pause()`, and `_pause()` unconditionally, then returns without updating `rsETHPrice`.

**`updateRSETHPrice()` is callable by anyone:** [5](#0-4) 

The function is `public whenNotPaused` with no role restriction. Any EOA or contract can call it at any time.

**Registration-time check provides no runtime protection:** [6](#0-5) 

`updatePriceOracleForValidated` validates the price only once at setup. A legitimately registered feed that later transiently returns 0 bypasses this check entirely.

## Impact Explanation

All user deposits (`LRTDepositPool`) and withdrawals (`LRTWithdrawalManager`) are paused. Users cannot deposit assets or initiate/complete withdrawals until an admin manually unpauses. This constitutes **temporary freezing of funds**, matching the Medium impact scope. The freeze duration is bounded only by admin response time.

## Likelihood Explanation

Chainlink returning `answer = 0` during an incomplete round is a documented edge case that has occurred on mainnet during oracle updates and network disruptions. No attacker capability beyond calling a public function is required. An attacker can monitor Chainlink round state off-chain and call `updateRSETHPrice()` opportunistically at the moment a round transition produces `answer = 0`. The attack requires no privileged access, no victim mistake, and no external protocol compromise — only a transient Chainlink behavior that is outside the protocol's control. The preconditions (`pricePercentageLimit > 0` and `highestRsethPrice > 0`) are expected to hold in any live deployment.

## Recommendation

Add the following validations inside `ChainlinkPriceOracle.getAssetPrice`:

```solidity
(uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

require(price > 0, "Chainlink: zero or negative price");
require(updatedAt != 0, "Chainlink: incomplete round");
require(answeredInRound >= roundId, "Chainlink: stale price");
require(block.timestamp - updatedAt <= MAX_STALENESS, "Chainlink: stale price");
```

This ensures a zero or stale price causes a revert rather than silently propagating into TVL calculations and triggering the auto-pause.

## Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// 1. Deploy a mock Chainlink feed returning answer=0
contract MockZeroFeed {
    function decimals() external pure returns (uint8) { return 8; }
    function latestRoundData() external pure returns (
        uint80, int256, uint256, uint256, uint80
    ) {
        return (1, 0, block.timestamp, block.timestamp, 1);
    }
}

// Fork test sequence:
// 1. Deploy MockZeroFeed on a mainnet fork
// 2. As LRTManager, call chainlinkPriceOracle.updatePriceFeedFor(stETH, address(mockZeroFeed))
//    (register when price is valid, then swap the underlying feed to MockZeroFeed)
// 3. Ensure rsETH totalSupply > 0 and highestRsethPrice > 0 (live protocol state)
// 4. Ensure pricePercentageLimit > 0 (expected in live deployment)
// 5. Call lrtOracle.updateRSETHPrice() as any EOA
// 6. Assert lrtDepositPool.paused() == true
// 7. Assert lrtWithdrawalManager.paused() == true
// 8. Assert lrtOracle.paused == true
//
// Fuzz variant: fuzz `answer` in [0, threshold] where threshold = price that causes
// newRsETHPrice to drop more than pricePercentageLimit below highestRsethPrice,
// and assert pause triggers for all such values.
```

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

**File:** contracts/LRTOracle.sol (L101-108)
```text
    function updatePriceOracleForValidated(address asset, address priceOracle) external onlyLRTAdmin {
        // Sanity check: oracle price must have precision between 1e16 and 1e19
        uint256 price = IPriceFetcher(priceOracle).getAssetPrice(asset);
        if (price > 1e19 || price < 1e16) {
            revert InvalidPriceOracle();
        }
        updatePriceOracleFor(asset, priceOracle);
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

**File:** contracts/LRTOracle.sol (L336-343)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
