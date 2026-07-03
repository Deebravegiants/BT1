### Title
No Staleness Check on Chainlink Price Feed Allows Stale LST Prices to Drive rsETH Minting — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards every return value except `price`. Neither `updatedAt` (the timestamp of the last answer) nor `answeredInRound` (the round in which the answer was computed) is validated. This is the direct analog of the Linea ENS bug: just as the ENS verifier accepted a proof carrying an arbitrary, unverified L2 block number, the LRT deposit flow accepts an arbitrary, unverified Chainlink price that may be arbitrarily stale.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` is the price source for every LST accepted by the L1 deposit pool:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();   // updatedAt, answeredInRound silently dropped
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

`latestRoundData()` returns five values: `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The contract silently discards `updatedAt` and `answeredInRound`, so:

- A feed that has not been updated for hours or days returns its last cached answer with no revert.
- A round that was started but never finalised (`answeredInRound < roundId`) also passes silently.

This price flows directly into rsETH minting:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [2](#0-1) 

`lrtOracle.getAssetPrice(asset)` delegates directly to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
// contracts/LRTOracle.sol L156-158
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [3](#0-2) 

The pool-level oracle `ChainlinkOracleForRSETHPoolCollateral` does add a partial guard (`answeredInRound < roundID`, `timestamp == 0`) but still omits the critical `block.timestamp − updatedAt > heartbeat` check:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L27-32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
// ← no: block.timestamp - timestamp > STALE_PERIOD check
``` [4](#0-3) 

---

### Impact Explanation

**Impact: Medium — Temporary freezing of funds / share mis-accounting leading toward protocol insolvency.**

If a Chainlink LST/ETH feed goes stale while the underlying LST price has fallen (e.g., a depeg event, a slashing event, or a network outage that prevents the feed from updating), the stale inflated price is used to compute `rsethAmountToMint`. Depositors receive more rsETH than the deposited collateral is worth at the current market price. This dilutes all existing rsETH holders and, if repeated or large enough, can push the protocol toward insolvency (rsETH backed by less ETH-equivalent value than its supply implies).

---

### Likelihood Explanation

Chainlink LST/ETH feeds (e.g., stETH/ETH, rETH/ETH) have heartbeat intervals of 24 hours and deviation thresholds of 0.5 %. During periods of high network congestion, oracle keeper failures, or rapid LST price movement, the feed can lag by hours. The attack path requires no special privilege: any depositor calling `depositAsset()` during a stale-feed window automatically receives excess rsETH. The window can last until the feed self-heals or an admin manually pauses the protocol.

---

### Recommendation

Add a configurable `stalePeriod` to `ChainlinkPriceOracle` and revert if the answer is too old:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Stale round");
require(updatedAt != 0, "Incomplete round");
require(block.timestamp - updatedAt <= stalePeriod, "Stale price");
```

Apply the same fix to `ChainlinkOracleForRSETHPoolCollateral.getRate()`, adding the `block.timestamp - timestamp <= stalePeriod` guard that is currently absent.

---

### Proof of Concept

1. Chainlink stETH/ETH feed last updated at `T − 25 h`; current stETH market price is 0.97 ETH (depeg), but the stale feed still reports 1.00 ETH.
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
3. `getRsETHAmountToMint` computes `(1000e18 × 1.00e18) / rsETHPrice` instead of `(1000e18 × 0.97e18) / rsETHPrice`, minting ~3 % excess rsETH.
4. Attacker immediately redeems or sells the excess rsETH, extracting value from existing holders.
5. No admin action, no special role, no front-running required — the stale price is returned by the on-chain feed itself. [1](#0-0) [5](#0-4)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
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
