Audit Report

## Title
Missing Chainlink `latestRoundData` Staleness and Validity Checks Allow Stale/Invalid Prices to Corrupt rsETH Exchange Rate - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards `roundId`, `updatedAt`, and `answeredInRound`, performing no staleness, incomplete-round, or non-positive price checks. A stale or zero price for any supported LST asset propagates through `LRTOracle._getTotalEthInProtocol()` into `rsETHPrice`, corrupting the exchange rate used for all deposits and withdrawals. The same repository already applies the correct validation pattern in `ChainlinkOracleForRSETHPoolCollateral`.

## Finding Description

In `contracts/oracles/ChainlinkPriceOracle.sol` at L52–54, `getAssetPrice()` discards all validation fields:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

No check is made for:
- `price > 0` — a zero answer (e.g., from an incomplete round) is silently returned as zero.
- `updatedAt != 0` — an incomplete round returns `updatedAt == 0` with an unreliable answer.
- `answeredInRound >= roundId` — a carried-over answer from a prior round indicates a stale price.

By contrast, `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol` at L30–32 correctly validates all three:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The corrupted price propagates as follows:

1. `ChainlinkPriceOracle.getAssetPrice()` returns stale/zero price.
2. `LRTOracle.getAssetPrice()` (L156–158) delegates to it.
3. `LRTOracle._getTotalEthInProtocol()` (L339, L343) multiplies `assetER * totalAssetAmt` for all supported assets.
4. `LRTOracle._updateRsETHPrice()` (L250) computes `newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply)`.
5. `rsETHPrice` is written with the corrupted value (L313).
6. `updateRSETHPrice()` (L87–89) is `public` and callable by anyone.

The existing `pricePercentageLimit` guard (L256–266, L273–281) provides only partial mitigation: it is unset (zero) by default, and even when set, only catches deviations exceeding the configured threshold — stale prices within the band are silently accepted and written.

The `updatePriceOracleForValidated()` sanity check (L103–106) only validates the price at oracle registration time, not at runtime.

## Impact Explanation

**High — Theft of unclaimed yield.**

A stale price within the `pricePercentageLimit` band is silently written as `rsETHPrice`. `LRTDepositPool.getRsETHAmountToMint()` (L520) computes `rsethAmountToMint = (amount * getAssetPrice(asset)) / rsETHPrice`. An inflated `rsETHPrice` causes depositors to receive fewer rsETH shares than owed (value extracted from new depositors). A deflated `rsETHPrice` causes depositors to receive more rsETH than owed, diluting existing holders' unclaimed yield.

**Medium — Temporary freezing of funds** (secondary path): a stale price that deviates beyond `pricePercentageLimit` triggers the downside-protection pause at L277–281, freezing deposits and withdrawals until an admin unpauses.

## Likelihood Explanation

Chainlink feeds go stale during Ethereum network congestion or feed deprecation. `updateRSETHPrice()` is permissionless — any external caller can invoke it during a staleness window. No special privileges, front-running, or economic attack are required. The attacker simply calls the public function while a feed is stale; the corrupted price is then used by all subsequent depositors and withdrawers until the next valid update.

## Recommendation

Apply the same validation pattern already present in `ChainlinkOracleForRSETHPoolCollateral.sol` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    require(price > 0, "Chainlink price <= 0");
    require(updatedAt != 0, "Incomplete round");
    require(answeredInRound >= roundId, "Stale price");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, add a per-feed heartbeat check (`block.timestamp - updatedAt <= MAX_STALENESS`) tuned to each feed's documented update frequency.

## Proof of Concept

**Step 1 — Setup**: Deploy a mock Chainlink aggregator for a supported LST (e.g., stETH) that returns a stale answer: `answeredInRound < roundId` (or `updatedAt == 0`), with a price value that differs from the true market price by an amount within `pricePercentageLimit`.

**Step 2 — Trigger**: Call `LRTOracle.updateRSETHPrice()` (public, no access control) while the mock feed returns the stale answer.

**Step 3 — Observe**: `rsETHPrice` is updated to a value derived from the stale LST price. Confirm via `lrtOracle.rsETHPrice()`.

**Step 4 — Impact**: Call `LRTDepositPool.depositAsset()` with a real user. The minted rsETH amount is computed as `(depositAmount * getAssetPrice(asset)) / rsETHPrice` — the corrupted `rsETHPrice` causes the user to receive an incorrect number of rsETH shares, demonstrating theft of unclaimed yield from either the depositor or existing holders depending on the direction of the stale deviation.

**Foundry fork test outline**:
```solidity
function testStaleChainlinkPriceCorruptsRsETHPrice() public {
    // 1. Fork mainnet, identify stETH Chainlink feed
    // 2. Mock latestRoundData to return answeredInRound = roundId - 1 (stale)
    //    with price 5% below current (within a 10% pricePercentageLimit)
    // 3. Call lrtOracle.updateRSETHPrice()
    // 4. Assert rsETHPrice decreased by ~5% * (stETH TVL / total TVL)
    // 5. Deposit stETH as user, assert rsETH minted > fair share (existing holders diluted)
}
```