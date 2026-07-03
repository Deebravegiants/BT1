Audit Report

## Title
Missing Staleness Validation on Chainlink `latestRoundData()` Enables Stale-Price Over-Minting of rsETH - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but discards all return values except `price`, applying no staleness guards whatsoever. When a Chainlink LST feed goes stale with an inflated last price, any unprivileged caller can invoke `LRTDepositPool.depositAsset()` to receive more rsETH than their deposit is worth, diluting all existing rsETH holders and constituting theft of unclaimed yield.

## Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the price as:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All five return values (`roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound`) are destructured, but only `price` is used. No `block.timestamp - updatedAt <= heartbeat` check, no `answeredInRound >= roundId` check, and no `updatedAt > 0` check are applied.

This price flows directly into `LRTDepositPool.getRsETHAmountToMint()`:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [2](#0-1) 

`lrtOracle.getAssetPrice(asset)` delegates to the registered `IPriceFetcher`, which for Chainlink-backed assets is `ChainlinkPriceOracle`: [3](#0-2) 

The minting path is fully reachable by any unprivileged user via `depositAsset()`: [4](#0-3) 

The same codebase demonstrates the correct pattern in `ChainlinkOracleForRSETHPoolCollateral`, which applies `answeredInRound < roundID`, `timestamp == 0`, and `ethPrice <= 0` guards — but this oracle is used only for pool collateral, not for the core deposit/mint path: [5](#0-4) 

The root cause is a missing validation layer in the protocol's own oracle wrapper code, not merely incorrect data from a third party. The SECURITY.md exclusion for "Incorrect data supplied by third-party oracles" does not apply here; the protocol is responsible for validating the data it consumes, and the note in SECURITY.md explicitly states oracle manipulation attacks are not excluded.

## Impact Explanation

If a Chainlink feed for a supported LST (e.g., stETH/ETH, ETHx/ETH) becomes stale with an inflated last reported price, `getAssetPrice()` returns that inflated value. The minting formula produces more rsETH than the deposited assets are worth. When the attacker redeems, they extract more ETH than they deposited, at the direct expense of all other rsETH holders whose share of the pool is diluted.

**Impact: High — Theft of unclaimed yield / dilution of existing rsETH holders.** This matches the allowed impact scope.

## Likelihood Explanation

Chainlink feeds go stale in realistic, non-adversarial conditions: network congestion preventing keeper transactions, sequencer downtime on L2 deployments, or a feed not updating because the deviation threshold was not crossed while the true price moved. An attacker monitoring on-chain oracle state can detect a stale feed and immediately call `depositAsset()` before the feed recovers. No privileged access is required.

**Likelihood: Medium** — requires a stale feed window, which occurs periodically in practice.

## Recommendation

Add staleness validation in `ChainlinkPriceOracle.getAssetPrice()`, consistent with the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

require(answeredInRound >= roundId, "Stale price: answeredInRound < roundId");
require(updatedAt > 0, "Stale price: incomplete round");
require(block.timestamp - updatedAt <= MAX_PRICE_AGE, "Stale price: too old");
require(price > 0, "Invalid price");
```

`MAX_PRICE_AGE` should be configured per feed based on its documented heartbeat (e.g., 3600 s for a 1-hour heartbeat feed, with a reasonable buffer).

## Proof of Concept

1. Chainlink's stETH/ETH feed last updated at `T - 2h` with price `1.05e18`. True current price is `1.00e18` (feed is stale and inflated).
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 100e18, 0, "")`.
3. `getRsETHAmountToMint(stETH, 100e18)` computes:
   - `getAssetPrice(stETH)` → returns stale `1.05e18` from `ChainlinkPriceOracle` (no staleness check).
   - `rsETHPrice` → e.g., `1.02e18`.
   - `rsethAmountToMint = (100e18 * 1.05e18) / 1.02e18 ≈ 102.94 rsETH`.
4. Fair value at true price: `(100e18 * 1.00e18) / 1.02e18 ≈ 98.04 rsETH`.
5. Attacker receives ~4.9 extra rsETH (~5% excess) at the expense of existing holders.
6. After the feed updates, attacker redeems 102.94 rsETH for ~105 ETH, having deposited 100 ETH worth of stETH — a ~5 ETH profit extracted from the pool.

**Foundry fork test plan:**
- Fork mainnet at a block where a supported LST Chainlink feed has not updated for longer than its heartbeat.
- Deploy or point to the existing `ChainlinkPriceOracle` with the stale feed registered.
- Call `depositAsset()` with the affected LST and record `rsethAmountToMint`.
- Compare against the fair-value mint amount computed using the true current price.
- Assert that `rsethAmountToMint > fairValueMint`, confirming over-minting.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L27-32)
```text
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```
