Audit Report

## Title
Missing Staleness Validation in `ChainlinkPriceOracle.getAssetPrice` Enables Phantom Fee Minting Against Inflated TVL — (`contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice` calls `latestRoundData()` but silently discards `updatedAt` and `answeredInRound`, accepting any price regardless of age or round completeness. When a supported LST's Chainlink feed goes stale while the asset's true ETH value has declined, the inflated stale price overstates `totalETHInProtocol`. The fee-minting branch in `_updateRsETHPrice` then treats the phantom TVL increase as real yield and mints rsETH to the treasury, permanently diluting all rsETH holders.

## Finding Description

**Root cause — `ChainlinkPriceOracle.getAssetPrice` (lines 49–55):**

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
```

All five return values of `latestRoundData()` — `(roundId, answer, startedAt, updatedAt, answeredInRound)` — are available, but only `price` is read. There is no `require(updatedAt >= block.timestamp - MAX_STALENESS)` and no `require(answeredInRound >= roundId)` guard. A feed that has not been updated for days returns its last cached price without any revert.

**Contrast with the pool-side oracle (`ChainlinkOracleForRSETHPoolCollateral.sol`, lines 27–32):**

```solidity
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The production LST pricing oracle has none of these protections.

**Fee-minting path:**

`_getTotalEthInProtocol` (lines 331–349) iterates every supported asset and calls `getAssetPrice(asset)`, which routes to `ChainlinkPriceOracle.getAssetPrice`. The stale inflated price is multiplied by total deposited amounts, overstating `totalETHInProtocol`. In `_updateRsETHPrice` (lines 244–247), if `totalETHInProtocol > previousTVL`, the difference is treated as real yield and a protocol fee is computed. The fee is then minted to the treasury as rsETH (lines 299–308).

**Why existing guards are insufficient:**

1. **`pricePercentageLimit`**: Its default/unset value is `0`, providing zero protection. Even when set, stale-price inflations within the configured limit pass through and trigger fee minting. The threshold revert (lines 252–266) only fires for large price spikes.
2. **`maxFeeMintAmountPerDay`**: If set to `0`, `_checkAndUpdateDailyFeeMintLimit` would revert any fee mint. However, for the protocol to collect fees at all, this must be set to a non-zero value — the normal operating configuration. Under that configuration, phantom fees up to the daily cap are minted without restriction.
3. **`updateRSETHPrice()` is permissionless** (line 87): any EOA can trigger the fee-minting path at will, requiring no special role or capital.

## Impact Explanation

When a Chainlink feed for a supported LST is stale and the asset's true ETH value has fallen below the last reported price, calling `updateRSETHPrice()` causes the protocol to mint rsETH to the treasury against TVL that does not exist. Every existing rsETH holder's share of the underlying ETH is permanently diluted. This is a direct, concrete instance of **High — Theft of unclaimed yield**: yield that belongs to rsETH holders is instead captured by the treasury via phantom fee minting.

## Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 24 h for many LST/ETH feeds). Network congestion, Chainlink node issues, or feed deprecation can cause staleness. The attack requires no special role, no front-running, and no capital — only the ability to call a public function. The precondition (a stale feed while the asset's true price has declined) is a realistic, non-negligible operational scenario. The attack is repeatable every time the feed remains stale.

## Recommendation

Add a configurable `MAX_STALENESS` constant and validate `updatedAt`, `answeredInRound`, and `price` in `ChainlinkPriceOracle.getAssetPrice`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Stale price");
require(updatedAt != 0, "Incomplete round");
require(block.timestamp - updatedAt <= MAX_STALENESS, "Price too old");
require(price > 0, "Invalid price");
```

`MAX_STALENESS` should be configurable per feed to accommodate different heartbeat intervals.

## Proof of Concept

```solidity
// Foundry test (no mainnet fork required)
contract StalePriceTest is Test {
    MockChainlinkFeed feed;       // returns fixed answer with configurable updatedAt
    ChainlinkPriceOracle oracle;
    LRTOracle lrtOracle;
    // ... minimal protocol stack setup

    function test_staleOraclePhantomFee() public {
        // 1. Configure feed: price = 1.05e18, updatedAt = 48 hours ago
        feed.setAnswer(1.05e18, block.timestamp - 48 hours);

        // 2. True market price has dropped to 1.00e18, but feed is stale

        // 3. Record treasury rsETH balance
        uint256 treasuryBefore = rsETH.balanceOf(treasury);

        // 4. Any EOA calls the permissionless function
        vm.prank(address(0xdead));
        lrtOracle.updateRSETHPrice();

        // 5. Treasury received rsETH despite no real yield
        assertGt(rsETH.balanceOf(treasury), treasuryBefore);
    }
}
```

The mock feed returns a stale inflated price; `_getTotalEthInProtocol` overstates TVL; `rewardAmount > 0`; fee is minted to treasury. No real yield accrued.