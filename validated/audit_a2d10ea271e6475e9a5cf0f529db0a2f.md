Audit Report

## Title
Missing Chainlink Round Validation in `ChainlinkPriceOracle.getAssetPrice` Enables Permissionless Protocol Auto-Pause — (`contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice` calls `latestRoundData()` and casts the raw `answer` directly to `uint256` without validating `updatedAt`, `answer > 0`, or `answeredInRound >= roundId`. During a Chainlink incomplete round (`updatedAt=0, answer=0`), the function silently returns `0`. This zero price deflates `_getTotalEthInProtocol()`, drives `newRsETHPrice` to near-zero, and — because `updateRSETHPrice()` is a permissionless `public` function — any external caller can trigger the downside-protection auto-pause, freezing `LRTDepositPool` and `LRTWithdrawalManager`.

## Finding Description

**Root cause — `ChainlinkPriceOracle.getAssetPrice` (lines 49–55):**

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

No check for `updatedAt == 0` (incomplete round), `price <= 0` (invalid/zero price), or `answeredInRound < roundId` (stale round). When `answer=0`, `uint256(0)` is returned without revert.

**Contrast with sibling oracle `ChainlinkOracleForRSETHPoolCollateral.getRate` (lines 30–32):**

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

The protocol already knows to guard these cases — the guard is simply absent from `ChainlinkPriceOracle`.

**Propagation through `_getTotalEthInProtocol` (lines 336–343):**

`assetER = getAssetPrice(asset)` returns `0` for the affected asset. `totalAssetAmt.mulWad(0) == 0`, zeroing that asset's entire ETH contribution and deflating `totalETHInProtocol`. [3](#0-2) 

**Auto-pause trigger in `_updateRsETHPrice` (lines 270–281):**

The deflated `totalETHInProtocol` produces `newRsETHPrice ≈ 0`. With `pricePercentageLimit > 0` and `highestRsethPrice > 0`, `diff > pricePercentageLimit.mulWad(highestRsethPrice)` evaluates to `true`, and the protocol pauses `LRTDepositPool`, `LRTWithdrawalManager`, and itself. [4](#0-3) 

**Permissionless entrypoint (line 87):**

`updateRSETHPrice()` is `public whenNotPaused` with no role restriction — callable by any EOA or contract. [5](#0-4) 

## Impact Explanation

When triggered, `LRTDepositPool.pause()` and `LRTWithdrawalManager.pause()` are called, halting all deposits, withdrawals, and claims. Unpausing requires `onlyLRTAdmin` intervention. Until admin acts, all user fund flows are frozen. This matches **Medium: Temporary freezing of funds**.

## Likelihood Explanation

Chainlink incomplete rounds (`updatedAt=0`) are a documented, non-attacker-controlled Chainlink infrastructure event — rare but real and locally reproducible with a mock feed. The attacker's role is minimal: observe the feed state and call the public `updateRSETHPrice()`. No special permissions, no front-running, no governance capture is required. Likelihood is **Low** (rare external condition), but the path is fully concrete.

## Recommendation

Add the same three guards present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice`:

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

## Proof of Concept

1. Deploy a mock Chainlink feed returning `(roundId=1, answer=0, startedAt=0, updatedAt=0, answeredInRound=1)`.
2. Register the mock feed via `ChainlinkPriceOracle.updatePriceFeedFor(asset, mockFeed)` (requires `onlyLRTManager` — setup step, not attacker action).
3. Register `ChainlinkPriceOracle` as the price oracle for that asset in `LRTOracle` (admin setup).
4. Set `pricePercentageLimit = 1e16` (1%) via `LRTOracle.setPricePercentageLimit`.
5. Ensure `rsETH.totalSupply() > 0` and `highestRsethPrice > 0` (normal protocol state after first deposit).
6. Any EOA calls `lrtOracle.updateRSETHPrice()`.

**Expected result:**
- `ChainlinkPriceOracle.getAssetPrice` returns `0` (no revert).
- `_getTotalEthInProtocol` returns a deflated value.
- `newRsETHPrice << highestRsethPrice`, triggering `isPriceDecreaseOffLimit = true`.
- `LRTDepositPool.paused() == true`, `LRTWithdrawalManager.paused() == true`.

**Differential:** Replacing `ChainlinkPriceOracle` with `ChainlinkOracleForRSETHPoolCollateral` causes `getRate()` to revert with `IncompleteRound()`, preventing the pause from being triggered.

### Citations

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

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
