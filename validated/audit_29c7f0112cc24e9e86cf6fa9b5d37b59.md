### Title
Unsafe `int256` to `uint256` Cast of Chainlink Price Without Negativity Check Can Freeze Protocol - (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` casts the `int256 price` returned by Chainlink's `latestRoundData()` directly to `uint256` without first validating that the value is positive. If Chainlink returns a zero or negative price, the bitwise reinterpretation of a negative `int256` as `uint256` produces a value near `2**256`. The subsequent multiplication by `1e18` then overflows and reverts under Solidity 0.8's checked arithmetic, causing every protocol function that depends on `getAssetPrice()` to revert.

---

### Finding Description

In `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

There is no guard on `price`. If `price` is negative (e.g., `-1`), then `uint256(-1) = 2**256 - 1`. Multiplying that by `1e18` overflows and reverts in Solidity 0.8.

The same codebase already applies the correct guard in `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
if (ethPrice <= 0) revert InvalidPrice();
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / ...;
``` [2](#0-1) 

The inconsistency confirms the developers are aware of the pattern but omitted it in `ChainlinkPriceOracle`.

The revert propagates through the following call chains:

**Chain 1 — Price update:**
`LRTOracle.updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice()` → **revert** [3](#0-2) 

**Chain 2 — Deposits:**
`LRTDepositPool.depositETH()` / `depositAsset()` → `_beforeDeposit()` → `getRsETHAmountToMint()` → `lrtOracle.getAssetPrice(asset)` → **revert** [4](#0-3) 

**Chain 3 — Withdrawals:**
`LRTWithdrawalManager.initiateWithdrawal()` → `getExpectedAssetAmount()` → `lrtOracle.getAssetPrice(asset)` → **revert** [5](#0-4) 

**Chain 4 — Unlock queue:**
`LRTWithdrawalManager.unlockQueue()` → `_createUnlockParams()` → `lrtOracle.getAssetPrice(asset)` → **revert** [6](#0-5) 

---

### Impact Explanation

If any supported asset's Chainlink feed returns a non-positive price, the entire protocol seizes:

- `updateRSETHPrice()` reverts — rsETH price cannot be updated.
- `depositETH()` and `depositAsset()` revert — users cannot deposit.
- `initiateWithdrawal()` reverts — users cannot queue new withdrawals.
- `unlockQueue()` reverts — operators cannot unlock pending withdrawals.

Funds already committed to pending withdrawal requests are temporarily frozen until the feed recovers or the oracle is replaced via governance. This matches the **Medium — Temporary freezing of funds** impact class.

---

### Likelihood Explanation

Chainlink price feeds for ETH/LST assets do not routinely return negative values, but the scenario is not theoretical:

- Chainlink has historically returned stale, zero, or anomalous values during oracle incidents.
- The contract applies zero validation, so any single-block anomaly is sufficient to trigger the freeze.
- The same codebase already guards against this in `ChainlinkOracleForRSETHPoolCollateral`, confirming the developers recognise the risk.
- No privileged access is required; the freeze is triggered automatically the moment any downstream caller (depositor, withdrawer, or public `updateRSETHPrice()` caller) invokes a function that reads the affected feed.

---

### Recommendation

Add a positivity check before the cast, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
if (price <= 0) revert InvalidPrice();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [7](#0-6) 

Additionally, consider adding staleness checks (`answeredInRound >= roundId`, `updatedAt != 0`) consistent with `ChainlinkOracleForRSETHPoolCollateral`.

---

### Proof of Concept

1. A supported asset's Chainlink feed (e.g., stETH/ETH) returns `price = -1` for one block due to an oracle incident.
2. Any user calls `LRTDepositPool.depositETH(minRSETH, "")`.
3. Execution reaches `ChainlinkPriceOracle.getAssetPrice(stETH)`.
4. `uint256(-1) = 2**256 - 1`; `(2**256 - 1) * 1e18` overflows → revert.
5. The deposit reverts. Simultaneously, `initiateWithdrawal`, `unlockQueue`, and `updateRSETHPrice` all revert for the same reason.
6. All user-facing protocol operations are frozen for the duration of the anomalous price report. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
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

**File:** contracts/LRTOracle.sol (L331-344)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
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

**File:** contracts/LRTWithdrawalManager.sol (L590-593)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));

        // calculate underlying asset amount to receive based on rsETH amount and asset exchange rate
        underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

**File:** contracts/LRTWithdrawalManager.sol (L846-850)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
```
