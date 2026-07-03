Audit Report

## Title
Missing Staleness Checks in `ChainlinkPriceOracle.getAssetPrice()` Allows Stale Price Acceptance - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards `roundId`, `updatedAt`, and `answeredInRound`, accepting stale or incomplete Chainlink prices without any validation. This stale price propagates into `LRTOracle._updateRsETHPrice()`, which is callable by any unprivileged address, enabling either incorrect rsETH pricing (theft/insolvency) or a spurious protocol-wide auto-pause (temporary fund freeze).

## Finding Description
In `contracts/oracles/ChainlinkPriceOracle.sol` at line 52, `getAssetPrice()` fetches the Chainlink price as:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All five return values are available per the interface declared at lines 14–17, but only `answer` is used. There is no check that `updatedAt > 0` (round is complete), `answeredInRound >= roundId` (answer is not from a prior round), or `price > 0` (answer is valid). [2](#0-1) 

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same repository performs all three checks:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [3](#0-2) 

The stale price returned by `ChainlinkPriceOracle.getAssetPrice()` is consumed by `LRTOracle.getAssetPrice()`, which delegates directly to the registered `IPriceFetcher`: [4](#0-3) 

That price is then used in `_getTotalEthInProtocol()` to compute `totalETHInProtocol`: [5](#0-4) 

Which feeds directly into `newRsETHPrice`: [6](#0-5) 

`updateRSETHPrice()` is a public, permissionless function — no role check, only `whenNotPaused`: [7](#0-6) 

Existing guards are insufficient: the `pricePercentageLimit` check only fires *after* the stale price has already been accepted and compared against `highestRsethPrice`; it does not prevent the stale price from being used.

## Impact Explanation

**Medium — Temporary freezing of funds (most directly reachable):** If a Chainlink feed returns a stale price that is sufficiently lower than `highestRsethPrice`, the auto-pause logic at lines 273–281 triggers, pausing `lrtDepositPool`, `withdrawalManager`, and `LRTOracle` simultaneously, freezing all deposits and withdrawals until an admin manually unpauses. [8](#0-7) 

**Critical — Theft of depositor value / protocol insolvency (higher-severity path):** If the stale price is artificially high (e.g., Chainlink heartbeat missed during a market crash), `totalETHInProtocol` is overstated, `rsETHPrice` is set above actual backing, new depositors receive fewer rsETH than owed (direct theft of depositor value), and existing rsETH becomes undercollateralized (protocol insolvency). [9](#0-8) 

## Likelihood Explanation
Chainlink feeds can return stale data during network congestion, sequencer downtime (L2), or heartbeat expiry without a deviation trigger — all documented operational risks. No special privileges are required: any external caller can invoke `updateRSETHPrice()` at any time, including during a staleness window. The attacker needs only to observe a stale feed and call the public function, making exploitation straightforward and repeatable.

## Recommendation
Apply the same staleness checks already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    require(answeredInRound >= roundId, "Stale price");
    require(updatedAt > 0, "Incomplete round");
    require(price > 0, "Invalid price");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Optionally add a per-feed heartbeat check: `require(block.timestamp - updatedAt <= MAX_STALENESS, "Price too old")`.

## Proof of Concept

1. Deploy a mock `AggregatorV3Interface` that returns `answeredInRound < roundId` (or `updatedAt == 0`, or a negative `price`).
2. Register it as the price feed for a supported asset via `ChainlinkPriceOracle.updatePriceFeedFor()`.
3. Call `LRTOracle.updateRSETHPrice()` from any EOA.
4. Observe that `getAssetPrice()` returns the stale/invalid value without reverting (no staleness check fires).
5. Observe `rsETHPrice` is updated to a value derived from the stale price, or the protocol is auto-paused if the stale price is sufficiently below `highestRsethPrice`.

**Foundry fork test plan:**
- Fork mainnet at a block where a Chainlink feed's `answeredInRound < roundId`.
- Call `updateRSETHPrice()` and assert `rsETHPrice` was set to an incorrect value, or assert the protocol was incorrectly paused.
- Confirm the same call reverts after applying the recommended fix.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L14-17)
```text
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);
```

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
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

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
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

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
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
