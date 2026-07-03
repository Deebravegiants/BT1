Audit Report

## Title
Missing Chainlink Price Feed Integrity Validation Allows Stale/Invalid Prices to Corrupt rsETH Rate - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards every return value except `price`, performing no staleness, round-completeness, or positivity checks. Because `LRTOracle.updateRSETHPrice()` is a public function callable by any address, an unprivileged actor can trigger an rsETH price update while a Chainlink feed is stale or returning an invalid answer, corrupting the protocol-wide `rsETHPrice` used to mint rsETH for all depositors. The same codebase already implements all three required checks in `ChainlinkOracleForRSETHPoolCollateral.sol`, confirming the protocol is aware of the requirement.

## Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads from Chainlink but discards every field except `price`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L52-54
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

Three integrity checks are absent:

| Check | `ChainlinkPriceOracle` | `ChainlinkOracleForRSETHPoolCollateral` |
|---|---|---|
| `price > 0` | Missing | `if (ethPrice <= 0) revert InvalidPrice();` |
| Round completeness | Missing | `if (answeredInRound < roundID) revert StalePrice();` |
| Timestamp validity | Missing | `if (timestamp == 0) revert IncompleteRound();` |

The stale/invalid price propagates through the public call chain:

1. `LRTOracle.updateRSETHPrice()` (public, no role required) → `_updateRsETHPrice()`
2. `_updateRsETHPrice()` calls `_getTotalEthInProtocol()`
3. `_getTotalEthInProtocol()` calls `getAssetPrice(asset)` for every supported asset, multiplying the stale price by total asset deposits to compute `totalETHInProtocol`
4. `newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply)` is written to `rsETHPrice`

The corrupted `rsETHPrice` is then used directly in `LRTDepositPool.getRsETHAmountToMint()`:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**Stale high price scenario:** A Chainlink LST/ETH feed goes stale while reporting a pre-depeg high price. An attacker calls `updateRSETHPrice()`. `totalETHInProtocol` is inflated, `newRsETHPrice` is set above its true value. Subsequent depositors receive fewer rsETH tokens than they are entitled to — their deposited value is redistributed to existing holders who can redeem at the inflated rate.

**Zero/near-zero price scenario:** A deprecated or broken feed returns `answer = 0`. `totalETHInProtocol` collapses for that asset's contribution. If the price drop exceeds `pricePercentageLimit`, the downside protection branch executes:
```solidity
// LRTOracle.sol L277-281
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
```
This pauses deposits and withdrawals for all users until an admin manually unpauses.

**Existing mitigations are insufficient:** The `pricePercentageLimit` upside check reverts non-manager callers only if the price increase exceeds the configured threshold, and only if `pricePercentageLimit > 0`. A stale price within the threshold window passes through unchecked. The `updatePriceOracleForValidated` sanity check (price between `1e16` and `1e19`) runs only at oracle registration time, not on each price update.

## Impact Explanation

**Primary — High: Theft of unclaimed yield.** When a stale high price is committed via `updateRSETHPrice()`, new depositors receive fewer rsETH tokens than the fair exchange rate entitles them to. The shortfall accrues to existing rsETH holders who redeem at the inflated rate. This is a direct, quantifiable transfer of depositor value to existing holders, matching the "Theft of unclaimed yield" impact class.

**Secondary — Medium: Temporary freezing of funds.** A zero or near-zero price from a broken/deprecated feed, when committed via the public `updateRSETHPrice()`, triggers the downside protection pause, freezing all deposits and withdrawals until admin intervention.

## Likelihood Explanation

Chainlink feeds go stale during Ethereum network congestion, oracle node outages, and feed deprecation events — all historically observed conditions. The attacker requires no privileged access, no capital, and no front-running. The only required action is calling the public `updateRSETHPrice()` at any point while the feed is stale. The window of opportunity persists for the entire duration of the staleness event. The attack is repeatable across any supported LST asset whose Chainlink feed experiences staleness.

## Recommendation

Apply the same three integrity checks already present in `ChainlinkOracleForRSETHPoolCollateral.sol` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Optionally add a heartbeat check: `require(block.timestamp - updatedAt <= MAX_DELAY)`.

## Proof of Concept

**Stale price / theft of yield:**

1. Deploy a mock Chainlink aggregator that returns a stale answer: `roundId = 5`, `answeredInRound = 4` (stale), `price = 1.05e18` (pre-depeg high), `updatedAt = block.timestamp - 25 hours`.
2. Register the mock as the price feed for a supported LST via `ChainlinkPriceOracle.updatePriceFeedFor()`.
3. Call `LRTOracle.updateRSETHPrice()` from any EOA.
4. Observe `rsETHPrice` is set using the stale `1.05e18` price instead of the true current price.
5. Call `LRTDepositPool.depositAsset()` with 1 LST. Observe `rsethAmountToMint = (1e18 * 1.05e18) / rsETHPrice` is lower than the fair amount computed with the true price.
6. Confirm the depositor received fewer rsETH tokens than entitled.

**Zero price / temporary freeze:**

1. Deploy a mock aggregator returning `price = 0`, `updatedAt = block.timestamp`, `answeredInRound = roundId`.
2. Register as price feed for a major supported LST.
3. Call `LRTOracle.updateRSETHPrice()` from any EOA.
4. If `pricePercentageLimit > 0` and the resulting price drop exceeds the limit, observe `lrtDepositPool.paused() == true` and `withdrawalManager.paused() == true`.
5. Confirm all user deposits and withdrawals are frozen until admin unpause.