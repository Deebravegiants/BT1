### Title
Missing Chainlink Price Staleness and Validity Checks Allow Stale/Zero Prices to Corrupt rsETH Minting and Withdrawal Accounting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all validity fields (`updatedAt`, `answeredInRound`, `roundId`) and performs no check on whether the returned `price` is positive. A stale or zero price from Chainlink is silently accepted and propagated into every user-facing deposit, withdrawal, and rsETH price update path.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the LST/ETH exchange rate from a Chainlink aggregator:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-L55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (, int256 price,,,) = priceFeed.latestRoundData();   // updatedAt, answeredInRound, roundId all discarded

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

No check is performed on:
- `updatedAt` — whether the price was updated within the expected heartbeat window (staleness)
- `answeredInRound < roundId` — whether the round is complete
- `price <= 0` — whether the price is valid

By contrast, the pool-level oracle wrapper in the same repository correctly validates all three:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L26-L36
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

`ChainlinkPriceOracle` is the oracle used for all supported LST assets (stETH, rETH, ETHx, etc.) in the core protocol, not the pool. The missing checks apply to the critical path.

---

### Impact Explanation

`getAssetPrice()` is called in three critical flows:

**1. Deposit flow** — `LRTDepositPool.depositETH()` / `depositAsset()` → `_beforeDeposit()` → `getRsETHAmountToMint()` → `lrtOracle.getAssetPrice(asset)`: [3](#0-2) 

If the Chainlink feed returns `price = 0` (e.g., during a circuit-breaker event or oracle outage), `getRsETHAmountToMint` returns 0, causing every deposit to revert with `MinimumAmountToReceiveNotMet` — a complete DoS on deposits while user funds are locked in the protocol.

**2. rsETH price update** — `LRTOracle.updateRSETHPrice()` → `_getTotalEthInProtocol()` → `getAssetPrice()` for each supported asset: [4](#0-3) 

A stale price silently inflates or deflates `totalETHInProtocol`, causing `rsETHPrice` to be computed incorrectly. This misprices all subsequent deposits and withdrawals and corrupts the fee-minting calculation.

**3. Withdrawal unlock** — `LRTWithdrawalManager._createUnlockParams()` → `lrtOracle.getAssetPrice(asset)`: [5](#0-4) 

A stale asset price used in `_calculatePayoutAmount` causes users to receive incorrect asset amounts when their withdrawal is unlocked.

The combined impact is **temporary freezing of funds** (deposits/withdrawals DoS when oracle returns 0) and **share/asset mis-accounting** (stale price corrupts rsETH minting rate and withdrawal payouts).

---

### Likelihood Explanation

Chainlink LST/ETH feeds (stETH/ETH, rETH/ETH) have historically experienced delayed updates during periods of extreme network congestion or oracle node issues. Chainlink's own documentation warns that `latestRoundData()` can return stale data and recommends staleness checks. The likelihood is **Low** but non-negligible given the protocol's TVL and the historical precedent of Chainlink feed delays.

---

### Recommendation

Add staleness and validity checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    if (block.timestamp - updatedAt > HEARTBEAT_TIMEOUT) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Each asset's heartbeat timeout should be stored and configurable, as different Chainlink feeds have different update frequencies.

---

### Proof of Concept

1. Chainlink's stETH/ETH feed enters a delayed-update state (e.g., network congestion); `updatedAt` is 4 hours old but `latestRoundData()` does not revert — it returns the last cached price.
2. Any caller invokes `LRTDepositPool.depositAsset(stETH, amount, 0, "")`.
3. `_beforeDeposit` → `getRsETHAmountToMint` → `LRTOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` returns the stale price without any revert.
4. rsETH is minted at the stale rate, silently mis-accounting the depositor's share relative to the true current stETH/ETH rate.

Alternatively, if the feed returns `price = 0`:
- `uint256(0) * 1e18 / decimals = 0`
- `rsethAmountToMint = (amount * 0) / rsETHPrice = 0`
- `0 < minRSETHAmountExpected` → revert `MinimumAmountToReceiveNotMet`
- All deposits are frozen until the oracle recovers. [6](#0-5) [1](#0-0)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-36)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
```

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTDepositPool.sol (L648-669)
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
```

**File:** contracts/LRTOracle.sol (L336-344)
```text
        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

```

**File:** contracts/LRTWithdrawalManager.sol (L846-850)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
```
