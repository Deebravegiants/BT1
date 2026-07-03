Audit Report

## Title
Missing Chainlink `latestRoundData()` Return Value Validation Enables rsETH Price Manipulation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

## Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` and casts the returned `int256 price` directly to `uint256` with no checks for a zero/negative price, stale round, or incomplete round. When a Chainlink feed returns `price = 0` (circuit-breaker floor), the affected LST contributes zero ETH to `_getTotalEthInProtocol()`, deflating `rsETHPrice` in storage. Because `updateRSETHPrice()` is public and `pricePercentageLimit` defaults to `0` (disabling the downside-pause guard), any unprivileged caller can commit the deflated price and then deposit a correctly-priced asset to mint excess rsETH, stealing value from existing rsETH holders.

## Finding Description

**Root cause — no validation in `getAssetPrice()`:** [1](#0-0) 

The function discards all five return values except `price`, then casts it unconditionally to `uint256`. Three checks are absent:
- `price <= 0` — a Chainlink circuit-breaker floor can return `0`; `uint256(0) * 1e18 / decimals = 0`.
- `answeredInRound < roundId` — stale answer detection.
- `updatedAt == 0` — incomplete round detection.

The sister contract in the same repository performs all three checks correctly: [2](#0-1) 

**Exploit path:**

1. Chainlink feed for LST asset `X` hits its minimum-price circuit breaker and returns `price = 0`.
2. `getAssetPrice(X)` returns `0`.
3. Attacker calls `LRTOracle.updateRSETHPrice()` — it is `public` with only a `whenNotPaused` guard: [3](#0-2) 
4. `_getTotalEthInProtocol()` sums asset values; asset `X` contributes `0 ETH` regardless of its true balance: [4](#0-3) 
5. `newRsETHPrice = (totalETHInProtocol - fee) / rsethSupply` is deflated below the true backing ratio.
6. The downside-pause guard is inactive because `pricePercentageLimit` defaults to `0`: [5](#0-4) 
7. `rsETHPrice` is written to storage at the deflated value.
8. Attacker calls `depositAsset(Y, amount, 0, "")` for a correctly-priced asset `Y`. `getRsETHAmountToMint` computes: [6](#0-5) 
   `rsethAmountToMint = (amount * correctAssetPrice(Y)) / deflatedRsETHPrice` — more rsETH than fair value.
9. When the Chainlink feed recovers, the attacker redeems excess rsETH at the true backing ratio, extracting value from all other rsETH holders.

**Why existing guards fail:**
- The `pricePercentageLimit` downside-pause only fires when `pricePercentageLimit > 0`; its Solidity default is `0`, leaving it inactive until an admin explicitly sets it.
- `minRSETHAmountExpected` in `depositAsset` is attacker-controlled and set to `0`, so the slippage check does not protect other users.

## Impact Explanation

**High — Theft of unclaimed yield / dilution of existing rsETH holders' backing.**

When the attacker mints rsETH at a deflated price and later redeems at the recovered price, the excess rsETH is backed by value that belonged to existing holders. The magnitude of the theft is proportional to the TVL share of the affected LST (e.g., if asset `X` is 15% of TVL, `rsETHPrice` is deflated ~15%, and the attacker extracts ~17.6% more rsETH per unit deposited). This is a concrete, quantifiable loss to existing rsETH holders, not a hypothetical one.

## Likelihood Explanation

Chainlink circuit-breaker events (returning `0` or a min/max sentinel) are documented and have occurred on mainnet (LUNA crash, stETH depeg). The attack requires no special permissions: `updateRSETHPrice()` is public, `depositAsset()` is open to any user, and `pricePercentageLimit` is `0` by default. An attacker only needs to observe the on-chain Chainlink answer and act within the same block or shortly after the feed hits its floor.

## Recommendation

Add the following checks inside `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

if (price <= 0)                revert InvalidPrice();
if (updatedAt == 0)            revert IncompleteRound();
if (answeredInRound < roundId) revert StalePrice();
// Optionally: if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();

return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

Additionally, consider setting a non-zero `pricePercentageLimit` as a defense-in-depth measure so the downside-pause guard is active.

## Proof of Concept

**Minimal Foundry fork test outline:**

1. Fork mainnet at a block where a supported LST Chainlink feed is live.
2. Deploy a mock `AggregatorV3Interface` that returns `(roundId=1, price=0, startedAt=0, updatedAt=block.timestamp, answeredInRound=1)`.
3. Call `ChainlinkPriceOracle.updatePriceFeedFor(assetX, mockFeed)` as LRTManager.
4. Record `rsETHPrice` before: `uint256 priceBefore = lrtOracle.rsETHPrice()`.
5. Call `lrtOracle.updateRSETHPrice()` as the attacker (unprivileged EOA).
6. Assert `lrtOracle.rsETHPrice() < priceBefore` — price is deflated.
7. Call `lrtDepositPool.depositAsset(assetY, amount, 0, "")` as the attacker.
8. Assert `rsethMinted > (amount * correctAssetYPrice) / priceBefore` — excess rsETH minted.
9. Restore the real feed; call `lrtOracle.updateRSETHPrice()` again; assert attacker's rsETH is now worth more than deposited, at the expense of other holders' backing ratio.

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

**File:** contracts/LRTOracle.sol (L273-274)
```text
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
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
