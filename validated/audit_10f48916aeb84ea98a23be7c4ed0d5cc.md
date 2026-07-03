Audit Report

## Title
Missing Positivity Check on Chainlink `int256` Price Before `uint256` Cast Causes Overflow Revert - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` casts the `int256 price` returned by `latestRoundData()` directly to `uint256` with no guard. If Chainlink returns a zero or negative price, the cast produces a value at or near `2**256`, and the subsequent multiplication by `1e18` overflows under Solidity 0.8 checked arithmetic, reverting every protocol function that reads the oracle. The same codebase already applies the correct guard in `ChainlinkOracleForRSETHPoolCollateral.getRate()`, confirming developer awareness of the pattern.

## Finding Description

In `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

There is no check that `price > 0`. If `price == -1`, then `uint256(-1) == 2**256 - 1`; multiplying by `1e18` overflows and reverts. If `price == 0`, `getAssetPrice` returns `0`, causing a division-by-zero revert in callers such as `getExpectedAssetAmount` (`amount * rsETHPrice / 0`).

The contrast with `ChainlinkOracleForRSETHPoolCollateral.getRate()` is direct:

```solidity
if (ethPrice <= 0) revert InvalidPrice();
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / ...;
``` [2](#0-1) 

The revert propagates through four public call chains:

- **Price update:** `updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `getAssetPrice(asset)` → revert. [3](#0-2) 

- **Deposits:** `depositETH()` / `depositAsset()` → `getRsETHAmountToMint()` → `lrtOracle.getAssetPrice(asset)` → revert. [4](#0-3) 

- **Withdrawals:** `initiateWithdrawal()` → `getExpectedAssetAmount()` → `lrtOracle.getAssetPrice(asset)` → revert. [5](#0-4) 

- **Unlock queue:** `unlockQueue()` → `_createUnlockParams()` → `lrtOracle.getAssetPrice(asset)` → revert. [6](#0-5) 

No existing check in `ChainlinkPriceOracle` or `LRTOracle` intercepts a non-positive price before the overflow occurs. [7](#0-6) 

## Impact Explanation

**Medium — Temporary freezing of funds.** While the anomalous price persists, all deposits, all new withdrawal initiations, all unlock-queue operations, and all rsETH price updates revert. Assets already committed to pending withdrawal requests cannot be unlocked until the feed recovers or governance replaces the oracle. This matches the allowed impact class "Temporary freezing of funds."

## Likelihood Explanation

No privileged access is required. Any unprivileged caller invoking `depositETH`, `depositAsset`, `initiateWithdrawal`, `unlockQueue`, or the public `updateRSETHPrice` automatically triggers the revert the moment the affected Chainlink feed returns a non-positive value. Chainlink feeds have historically returned zero or anomalous values during oracle incidents. The `AggregatorV3Interface` returns `int256` precisely because the interface does not guarantee positivity; Chainlink's own documentation recommends checking for non-positive values. The inconsistency within this codebase confirms the developers recognise the risk.

## Recommendation

Add a positivity check before the cast, mirroring the pattern in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
if (price <= 0) revert InvalidPrice();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

Additionally, add staleness checks (`answeredInRound >= roundId`, `updatedAt != 0`) consistent with `ChainlinkOracleForRSETHPoolCollateral.getRate()`. [8](#0-7) 

## Proof of Concept

1. Deploy a mock `AggregatorV3Interface` whose `latestRoundData()` returns `price = -1` and `decimals() = 8`.
2. Register it as the price feed for a supported asset in `ChainlinkPriceOracle`.
3. Call `LRTDepositPool.depositAsset(asset, amount, minRSETH, "")` from any EOA.
4. Execution reaches `ChainlinkPriceOracle.getAssetPrice(asset)`: `uint256(-1) == 2**256 - 1`; `(2**256 - 1) * 1e18` overflows → revert.
5. Repeat for `initiateWithdrawal`, `unlockQueue`, and `updateRSETHPrice` — all revert identically.
6. Repeat with `price = 0`: `getAssetPrice` returns `0`; `getExpectedAssetAmount` divides by zero → revert.

A Foundry fork test can demonstrate steps 3–6 against the live contracts by overriding the Chainlink feed address with the mock via `vm.etch` or `vm.mockCall`.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-34)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
```

**File:** contracts/LRTOracle.sol (L339-339)
```text
            uint256 assetER = getAssetPrice(asset);
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTWithdrawalManager.sol (L593-593)
```text
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L848-848)
```text
            assetPrice: lrtOracle.getAssetPrice(asset),
```
