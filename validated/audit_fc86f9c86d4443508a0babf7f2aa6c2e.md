Audit Report

## Title
Chainlink Price Oracle Lacks Staleness and Validity Checks, Enabling Stale Price Exploitation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `price`, with no staleness check on `updatedAt`, no round completeness check, and no `price > 0` guard. This stale or zero price flows directly into rsETH minting and TVL accounting, allowing an attacker to over-mint rsETH during a feed staleness event, diluting existing holders.

## Finding Description
`ChainlinkPriceOracle.getAssetPrice()` at line 52 reads:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All of `roundId`, `startedAt`, `updatedAt`, and `answeredInRound` are discarded. No check is made that `updatedAt` is recent, that `answeredInRound >= roundId`, or that `price > 0`.

By contrast, the sister contract `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same repository explicitly performs all three checks:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

`LRTOracle.getAssetPrice()` delegates directly to `ChainlinkPriceOracle`: [3](#0-2) 

This stale price is consumed in two critical paths:

1. **rsETH minting** — `LRTDepositPool.getRsETHAmountToMint()` computes `(amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()`: [4](#0-3) 

2. **TVL / rsETH price update** — `LRTOracle._getTotalEthInProtocol()` sums `totalAssetAmt.mulWad(assetER)` using the same stale price: [5](#0-4) 

The `pricePercentageLimit` guard in `_updateRsETHPrice()` only triggers during explicit `updateRSETHPrice()` calls and does not protect the deposit path, which reads the live oracle price directly at mint time. [6](#0-5) 

Additionally, if `price` is zero (possible during a Chainlink incident), `uint256(0)` causes `getRsETHAmountToMint` to return 0, and with `minRSETHAmountExpected = 0`, the deposit proceeds, transferring the depositor's tokens while minting zero rsETH — a direct loss of depositor funds.

## Impact Explanation
**High — Theft of unclaimed yield.** When a Chainlink feed goes stale at a price above the true market price (e.g., stETH depegs while the feed is frozen), any depositor can call `depositAsset()` and receive more rsETH than the true ETH value of their deposit. This dilutes the rsETH/ETH backing ratio for all existing holders, constituting theft of unclaimed yield. The zero-price edge case additionally maps to direct loss of depositor funds (Low–Critical depending on conditions).

## Likelihood Explanation
Chainlink feeds go stale during sequencer outages (L2), network congestion, feed migrations, or circuit-breaker freezes during extreme volatility. No special permissions are required — any external caller can invoke `depositAsset()` or `depositETH()` at any time while the contract is unpaused. The staleness window is open for the entire duration of the feed outage. The exploit is repeatable and requires no victim mistakes.

## Recommendation
Apply the same validation pattern already present in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    if (block.timestamp - updatedAt > stalenessThreshold[asset]) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`stalenessThreshold` should be configurable per asset (different feeds have different heartbeat intervals, e.g., stETH/ETH is 24 hours on mainnet).

## Proof of Concept

1. Assume the stETH/ETH Chainlink feed goes stale at `1.05e18` (true market price drops to `0.95e18` due to a depeg event while the feed is frozen).
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 100e18, 0, "")`.
3. `_beforeDeposit` → `getRsETHAmountToMint` → `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale `1.05e18`.
4. `rsethAmountToMint = (100e18 * 1.05e18) / rsETHPrice` — attacker receives ~10.5% more rsETH than the true ETH value of their deposit.
5. Attacker requests withdrawal, redeeming rsETH at the correct (lower) TVL-backed price, extracting value from existing holders.

**Foundry fork test plan**: Fork mainnet, use `vm.mockCall` on the stETH/ETH Chainlink aggregator to return a stale `updatedAt` timestamp (e.g., `block.timestamp - 2 days`) with an inflated price. Call `depositAsset` as an unprivileged address and assert that `rsethAmountToMint` exceeds the fair value. Confirm no revert occurs in the current implementation, then apply the fix and confirm the call reverts with `StalePrice`.

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

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L252-266)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
