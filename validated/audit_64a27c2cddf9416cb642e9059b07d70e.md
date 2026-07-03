### Title
Chainlink `latestRoundData()` Revert Causes Protocol-Wide DOS on Deposits and Withdrawal Initiations - (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `priceFeed.latestRoundData()` with no try/catch and no fallback. If Chainlink's multisig blocks access to a price feed, the call reverts and propagates through `LRTOracle.getAssetPrice()` into every user-facing function that requires a live asset price, causing a temporary but complete DOS on deposits and new withdrawal initiations.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the asset price directly from the Chainlink aggregator with no error handling:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

`LRTOracle.getAssetPrice()` delegates directly to this oracle with no fallback:

```solidity
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [2](#0-1) 

This live call propagates into two critical user-facing paths:

**Path 1 — Deposits:**
`LRTDepositPool.depositAsset()` / `depositETH()` → `_beforeDeposit()` → `getRsETHAmountToMint()` → `lrtOracle.getAssetPrice(asset)`. [3](#0-2) 

**Path 2 — Withdrawal initiation:**
`LRTWithdrawalManager.initiateWithdrawal()` → `getExpectedAssetAmount()` → `lrtOracle.getAssetPrice(asset)`. [4](#0-3) 

**Path 3 — Instant withdrawals:**
`LRTWithdrawalManager.instantWithdrawal()` → `getExpectedAssetAmount()` → `lrtOracle.getAssetPrice(asset)`. [5](#0-4) 

**Path 4 — Price updates:**
`LRTOracle.updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `getAssetPrice(asset)` for every supported asset. [6](#0-5) 

There is no try/catch, no secondary oracle, and no cached fallback price anywhere in this call chain.

---

### Impact Explanation

If Chainlink's multisig blocks access to any supported asset's price feed (e.g., stETH/ETH, ETHx/ETH), `latestRoundData()` reverts. This causes:

- All new deposits (`depositAsset`, `depositETH`) to revert — users cannot enter the protocol.
- All new withdrawal initiations (`initiateWithdrawal`) to revert — users cannot queue new exits.
- All instant withdrawals (`instantWithdrawal`) to revert.
- `updateRSETHPrice()` to revert — the rsETH price becomes stale, blocking any downstream logic that depends on a fresh price.

Note: `completeWithdrawal()` for already-queued requests is unaffected because it uses the pre-committed `expectedAssetAmount` stored at initiation time and does not call `getAssetPrice()`.

**Impact: Temporary freezing of funds** — deposits and new withdrawal initiations are completely blocked for the duration of the feed outage.

---

### Likelihood Explanation

As documented by OpenZeppelin and acknowledged in the referenced audit finding, Chainlink multisigs can block access to price feeds at will. The protocol uses Chainlink feeds for multiple LST assets (stETH, ETHx, rETH, swETH) via `ChainlinkPriceOracle`. A block on any single feed is sufficient to DOS the entire deposit path and withdrawal initiation path for that asset. The protocol has no on-chain recovery path during the outage; governance must deploy and configure a replacement oracle, which takes time.

---

### Recommendation

Wrap `priceFeed.latestRoundData()` in a try/catch inside `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
try priceFeed.latestRoundData() returns (uint80, int256 price, uint256, uint256, uint80) {
    require(price > 0, "Invalid feed price");
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
} catch {
    revert("Chainlink feed unavailable");
}
```

Additionally, consider implementing a fallback oracle per asset in `LRTOracle` so that if the primary oracle reverts, a secondary price source (e.g., a TWAP or a fixed emergency price set by governance) is used, preventing a complete DOS.

---

### Proof of Concept

1. Protocol is live; `ChainlinkPriceOracle` is configured as the price oracle for stETH via `assetPriceOracle[stETH]`.
2. Alice calls `depositAsset(stETH, amount, minRSETH, "")`.
3. Chainlink's multisig blocks access to the stETH/ETH price feed.
4. `depositAsset` → `_beforeDeposit` → `getRsETHAmountToMint` → `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → `priceFeed.latestRoundData()` reverts.
5. Alice's deposit reverts. All subsequent deposits for stETH revert.
6. Alice tries `initiateWithdrawal(stETH, rsETHAmount, "")` → `getExpectedAssetAmount` → `lrtOracle.getAssetPrice(stETH)` → reverts.
7. `updateRSETHPrice()` also reverts, freezing the rsETH price at its last stored value.
8. The protocol remains in this state until governance deploys and configures a replacement oracle. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
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

**File:** contracts/LRTDepositPool.sol (L516-521)
```text
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L228-228)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
```

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
