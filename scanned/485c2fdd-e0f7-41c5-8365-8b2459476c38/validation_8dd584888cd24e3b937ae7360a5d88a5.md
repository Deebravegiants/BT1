### Title
Stale Chainlink Price Accepted Without `updatedAt` Validation — (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards every return value except `price`. No check is made against `updatedAt`, `answeredInRound`, or `roundId`. A stale price is consumed as if it were fresh, propagating incorrect exchange rates into every deposit, withdrawal, and rsETH price update in the protocol.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price with a destructured call that ignores all staleness indicators:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

`updatedAt`, `answeredInRound`, and `roundId` are all discarded. There is no comparison of `updatedAt` against `block.timestamp`, no `answeredInRound < roundId` guard, and no revert path for a stale feed.

This price is the sole input to `LRTOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [2](#0-1) 

`LRTOracle.getAssetPrice()` is consumed in three critical paths:

**1. Deposit minting** — `LRTDepositPool.getRsETHAmountToMint()`:
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

**2. Withdrawal sizing** — `LRTWithdrawalManager.getExpectedAssetAmount()`:
```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
``` [4](#0-3) 

**3. rsETH price update** — `LRTOracle._getTotalEthInProtocol()`:
```solidity
uint256 assetER = getAssetPrice(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [5](#0-4) 

For contrast, `ChainlinkOracleForRSETHPoolCollateral` (used for pool collateral) does implement partial guards (`answeredInRound < roundID`, `timestamp == 0`), but still omits a time-based staleness threshold: [6](#0-5) 

`ChainlinkPriceOracle` has none of these guards at all.

---

### Impact Explanation

**Stale price lower than real price (e.g., LST depegs temporarily then recovers, feed lags):**
- `getRsETHAmountToMint` inflates the rsETH minted per deposited LST unit.
- New depositors receive more rsETH than their deposit warrants, diluting all existing rsETH holders — equivalent to theft of accrued yield from existing holders.

**Stale price higher than real price:**
- `getExpectedAssetAmount` reduces the LST amount committed to a withdrawer.
- `_getTotalEthInProtocol` overstates TVL, causing `_updateRsETHPrice` to compute an inflated rsETH price, which then feeds back into subsequent deposits and withdrawals.

Both directions produce incorrect rsETH issuance or redemption amounts, directly harming depositors, withdrawers, or existing rsETH holders.

**Impact rating: High** — theft of unclaimed yield from existing rsETH holders via over-minting when a stale low price is consumed during deposit.

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 1 hour for ETH/USD, 24 hours for some LST feeds). Staleness occurs naturally during:
- Sequencer downtime (L2 deployments)
- Extreme network congestion preventing keeper transactions
- Feed deprecation or migration periods

No attacker action is required to cause staleness; an unprivileged depositor or withdrawer only needs to transact while the feed happens to be stale. Likelihood is **Medium** — not a constant condition, but a realistic and historically observed failure mode for Chainlink feeds.

---

### Recommendation

In `ChainlinkPriceOracle.getAssetPrice()`, capture and validate all staleness indicators:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (price <= 0) revert InvalidPrice();
    if (answeredInRound < roundId) revert StalePrice();
    if (block.timestamp - updatedAt > STALENESS_THRESHOLD) revert StalePrice(); // e.g. 1 hours

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Apply the same pattern to `ChainlinkOracleForRSETHPoolCollateral.getRate()`, which already has `answeredInRound < roundID` and `timestamp == 0` guards but is still missing the time-based threshold check. [7](#0-6) 

---

### Proof of Concept

1. The Chainlink feed for a supported LST (e.g., stETH/ETH) is not updated for 2 hours due to network congestion. Its `updatedAt` is now `block.timestamp - 7200`.
2. During this window the real stETH/ETH rate has moved from 0.999 to 1.001 (recovery), but the stale feed still reports 0.999.
3. An unprivileged depositor calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
4. `getRsETHAmountToMint` calls `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns the stale 0.999 price with no revert.
5. The depositor receives `(1000e18 × 0.999e18) / rsETHPrice` rsETH — computed using the stale low price — which is more rsETH than the real 1.001 rate would produce.
6. Existing rsETH holders are diluted by the excess minted rsETH, constituting theft of their accrued yield.
7. No privileged role, no oracle operator action, and no special timing beyond the natural staleness window is required.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTWithdrawalManager.sol (L593-593)
```text
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```
