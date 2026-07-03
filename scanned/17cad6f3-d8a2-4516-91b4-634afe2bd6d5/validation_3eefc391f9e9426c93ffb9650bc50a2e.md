### Title
Stale Chainlink Price Accepted Without Staleness Validation, Enabling Forced Protocol Pause - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but silently discards all safety return values (`roundId`, `startedAt`, `updatedAt`, `answeredInRound`), consuming only the raw `price`. This is the direct analog of TOKE-16: a price-safety signal is available from the data source but the caller ignores it. Because `updateRSETHPrice()` is a public, permissionless function, any external caller can trigger an `rsETHPrice` update using a stale feed value, which can activate the protocol's own downside-protection circuit-breaker and freeze deposits and withdrawals.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L52
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All five return values of `latestRoundData()` — `roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound` — are available, but only `answer` (`price`) is used. The staleness indicators `updatedAt` and `answeredInRound` are discarded without any check.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same repository explicitly validates all three safety conditions:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L27-32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

The stale price flows into `LRTOracle._getTotalEthInProtocol()`, which iterates all supported assets and calls `getAssetPrice(asset)` for each:

```solidity
// contracts/LRTOracle.sol L339
uint256 assetER = getAssetPrice(asset);
``` [3](#0-2) 

`_getTotalEthInProtocol()` is called by `_updateRsETHPrice()`, which computes `newRsETHPrice` and then applies the downside-protection logic:

```solidity
// contracts/LRTOracle.sol L270-281
if (newRsETHPrice < highestRsethPrice) {
    ...
    if (isPriceDecreaseOffLimit) {
        if (!lrtDepositPool.paused()) lrtDepositPool.pause();
        if (!withdrawalManager.paused()) withdrawalManager.pause();
        _pause();
        return;
    }
``` [4](#0-3) 

`updateRSETHPrice()` is public with no access control:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [5](#0-4) 

---

### Impact Explanation

When a Chainlink feed goes stale (e.g., during network congestion, sequencer downtime on L2, or feed deprecation), the last reported price remains frozen at its last value. If that stale price is lower than `highestRsethPrice` by more than `pricePercentageLimit`, calling `updateRSETHPrice()` will:

1. Compute a deflated `totalETHInProtocol` using the stale asset price.
2. Derive a `newRsETHPrice` below the downside threshold.
3. Trigger `lrtDepositPool.pause()`, `withdrawalManager.pause()`, and `_pause()` on the oracle.

This freezes all user deposits and withdrawals until an admin manually unpauses — a **temporary freezing of funds** (Medium). Even without hitting the threshold, a stale price causes incorrect rsETH minting amounts for depositors (Low: contract fails to deliver promised returns).

---

### Likelihood Explanation

- Chainlink feeds have documented heartbeat intervals (e.g., 24 hours for some LST feeds). A feed can remain stale for the full heartbeat window without triggering any on-chain revert.
- `updateRSETHPrice()` is callable by any unprivileged external account with no rate limiting.
- An attacker monitoring for a stale feed can call `updateRSETHPrice()` at the optimal moment to trigger the pause, requiring no capital and no special permissions.

---

### Recommendation

Add staleness and round-completeness checks in `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Stale price");
require(updatedAt != 0, "Incomplete round");
require(price > 0, "Invalid price");
require(block.timestamp - updatedAt <= MAX_STALENESS, "Price too old");
``` [6](#0-5) 

---

### Proof of Concept

1. A Chainlink LST/ETH feed (e.g., stETH/ETH) goes stale — its `updatedAt` timestamp is older than the heartbeat, but `latestRoundData()` still returns the last price without reverting.
2. The stale price is, say, 5% below the current true market price, exceeding `pricePercentageLimit`.
3. Attacker (any EOA) calls `LRTOracle.updateRSETHPrice()`.
4. `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `ChainlinkPriceOracle.getAssetPrice(stETH)` returns the stale low price.
5. `newRsETHPrice` is computed below `highestRsethPrice - pricePercentageLimit * highestRsethPrice`.
6. `isPriceDecreaseOffLimit == true` → `lrtDepositPool.pause()`, `withdrawalManager.pause()`, `_pause()` are called.
7. All user deposits (`depositAsset`, `depositETH`) and withdrawals (`initiateWithdrawal`, `instantWithdrawal`, `completeWithdrawal`) revert with `Paused` until an admin intervenes. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L231-231)
```text
        uint256 totalETHInProtocol = _getTotalEthInProtocol();
```

**File:** contracts/LRTOracle.sol (L270-282)
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
            }
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
