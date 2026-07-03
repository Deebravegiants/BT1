### Title
Stale Chainlink Price Accepted by `ChainlinkPriceOracle.getAssetPrice` Allows Any Caller to Trigger Protocol-Wide Pause — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice` performs no staleness validation on the Chainlink round data it consumes. When a feed goes stale, any unprivileged caller can invoke the public `LRTOracle.updateRSETHPrice()`, causing `_updateRsETHPrice` to compute an artificially depressed rsETH price that breaches the downside `pricePercentageLimit`, which automatically pauses `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle`, freezing all user deposits and withdrawals until an admin manually unpauses.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice` calls `latestRoundData()` but discards every field except `price`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
``` [1](#0-0) 

Neither `answeredInRound < roundId` (round-completeness staleness) nor `updatedAt` (timestamp staleness) is checked. By contrast, the sibling oracle `ChainlinkOracleForRSETHPoolCollateral.getRate` explicitly guards against this:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

`ChainlinkPriceOracle` is the oracle used by `LRTOracle` for supported LST assets. `_getTotalEthInProtocol` iterates every supported asset and calls `getAssetPrice(asset)` through this path: [3](#0-2) 

The result feeds directly into `newRsETHPrice`. If any asset's Chainlink feed is stale and its last-reported price is below the current market price (which is always true for yield-bearing LSTs, whose ETH-denominated price only increases), `totalETHInProtocol` is understated, and `newRsETHPrice` is depressed.

`_updateRsETHPrice` then evaluates the downside protection branch:

```solidity
if (newRsETHPrice < highestRsethPrice) {
    uint256 diff = highestRsethPrice - newRsETHPrice;
    bool isPriceDecreaseOffLimit =
        pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

    if (isPriceDecreaseOffLimit) {
        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!withdrawalManager.paused()) withdrawalManager.pause();
        _pause();
        return;
    }
``` [4](#0-3) 

`updateRSETHPrice()` is public and requires no role:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [5](#0-4) 

Any EOA can call it the moment a feed is stale enough to push the computed price below `highestRsethPrice - pricePercentageLimit * highestRsethPrice`.

---

### Impact Explanation

All three contracts — `LRTDepositPool`, `LRTWithdrawalManager`, and `LRTOracle` — are paused atomically. Users cannot deposit assets or initiate/claim withdrawals until an admin with `LRTAdmin` role manually unpauses each contract. This constitutes a **temporary freezing of funds** (Medium). [6](#0-5) 

---

### Likelihood Explanation

Chainlink feeds do go stale during network congestion or node outages. LST assets (stETH, cbETH, rETH, etc.) accrue staking yield continuously, so any stale price is always below the current market price. The required staleness duration depends on `pricePercentageLimit`: at a 1% limit (1e16) and ~5% APY, roughly 73 days of feed staleness suffices; at a 0.1% limit, only ~7 days. The trigger requires no capital, no privilege, and no front-running — just a public call.

---

### Recommendation

Add staleness validation to `ChainlinkPriceOracle.getAssetPrice`, mirroring the checks already present in `ChainlinkOracleForRSETHPoolCollateral`:

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

Optionally, add a configurable `heartbeat` per feed and check `block.timestamp - updatedAt > heartbeat`.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

// Fork mainnet at a recent block, then:
// 1. Warp block.timestamp forward past the Chainlink heartbeat for any
//    supported LST asset feed (e.g., stETH/ETH: 86400s heartbeat).
// 2. The feed's latestRoundData() still returns the last round's price,
//    which is lower than the current market price by accumulated yield.
// 3. Call updateRSETHPrice() as an unprivileged address.
// 4. Assert LRTDepositPool.paused() == true.
// 5. Assert a subsequent depositAsset() call reverts with "Pausable: paused".

function testStaleOraclePausesProtocol() public {
    // Warp past heartbeat — no new Chainlink round is published
    vm.warp(block.timestamp + 2 days);

    // Any unprivileged caller
    vm.prank(address(0xdead));
    lrtOracle.updateRSETHPrice();

    assertTrue(lrtDepositPool.paused(), "DepositPool should be paused");

    vm.expectRevert("Pausable: paused");
    lrtDepositPool.depositAsset(stETH, 1 ether, 0, "");
}
``` [7](#0-6) [5](#0-4)

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

**File:** contracts/LRTOracle.sol (L270-281)
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
