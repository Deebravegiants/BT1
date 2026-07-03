### Title
Unchecked Negative Chainlink `int256` Price Cast to `uint256` Corrupts rsETH Exchange Rate — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary
`ChainlinkPriceOracle.getAssetPrice()` casts the `int256 price` returned by Chainlink's `latestRoundData()` directly to `uint256` without verifying the value is positive. In Solidity 0.8.x, explicit casts do not revert on negative values — `uint256(int256(-1))` silently produces `type(uint256).max`. This corrupted price propagates into the rsETH exchange rate calculation, enabling protocol insolvency or temporary fund freezing.

---

### Finding Description
In `contracts/oracles/ChainlinkPriceOracle.sol`, the `getAssetPrice()` function fetches the Chainlink price and immediately casts it to `uint256` with no positivity guard:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

If Chainlink returns a negative `price` (e.g., during an oracle malfunction or extreme market event), `uint256(price)` wraps to a value near `type(uint256).max` (~1.157 × 10⁷⁷). This is not a theoretical concern — Chainlink's `int256 answer` is explicitly signed to accommodate such edge cases.

The same codebase already applies the correct guard in `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`:

```solidity
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

`ChainlinkPriceOracle` is the oracle adapter used for all supported LST assets in the core L1 protocol and is missing this check entirely.

---

### Impact Explanation
The corrupted price propagates through the following call chain:

1. `LRTOracle.getAssetPrice(asset)` calls `IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset)` — which resolves to `ChainlinkPriceOracle.getAssetPrice()`. [3](#0-2) 

2. `LRTOracle._getTotalEthInProtocol()` accumulates `assetER` (the corrupted price) multiplied by total asset deposits for each supported asset. [4](#0-3) 

3. `_updateRsETHPrice()` computes `newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply)` — an astronomically inflated value. [5](#0-4) 

**Scenario A — Manager calls `updateRSETHPriceAsManager()`:** The astronomical rsETH price is committed to storage. All subsequent deposits via `LRTDepositPool` use this price to compute `rsETHAmountToMint`, yielding near-zero rsETH for depositors. User funds are effectively stolen by the protocol — **Critical: direct theft of depositor funds / protocol insolvency**.

**Scenario B — Public `updateRSETHPrice()` is called:** If `pricePercentageLimit` is set (which it is for safety), the price increase check triggers a revert for non-managers, blocking all price updates. The rsETH price becomes stale, disrupting the deposit and withdrawal pipeline — **Medium: temporary freezing of funds**.

---

### Likelihood Explanation
Chainlink oracles returning non-positive prices is a documented edge case that has occurred in production (e.g., during oracle downtime, sequencer failures, or extreme market dislocations). The `int256` return type of `latestRoundData()` is explicitly designed to allow negative values. The missing check is a well-known vulnerability class in DeFi oracle integrations. Likelihood is **Low-Medium**: it requires an oracle anomaly, but no attacker action is needed — the condition can arise naturally.

---

### Recommendation
Add a positivity check before the cast in `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
if (price <= 0) revert InvalidPrice();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [6](#0-5) 

---

### Proof of Concept

1. Chainlink's `latestRoundData()` for a supported LST asset (e.g., stETH) returns `price = -1` due to an oracle anomaly.
2. `ChainlinkPriceOracle.getAssetPrice(stETH)` computes `uint256(-1) * 1e18 / 10**18` = `type(uint256).max` ≈ 1.157 × 10⁷⁷.
3. `LRTOracle._getTotalEthInProtocol()` returns an astronomically large `totalETHInProtocol`.
4. `_updateRsETHPrice()` sets `newRsETHPrice` to an astronomical value.
5. A manager calls `updateRSETHPriceAsManager()` — the corrupted price is stored as `rsETHPrice`.
6. A user deposits 1 ETH via `LRTDepositPool.depositETH()`. The `getRsETHAmountToMint()` calculation divides by the astronomical `rsETHPrice`, yielding `rsETHAmountToMint ≈ 0`.
7. The user's 1 ETH is accepted but they receive 0 rsETH — funds are permanently lost. [1](#0-0) [7](#0-6)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L32-32)
```text
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L331-349)
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

            unchecked {
                ++assetIdx;
            }
        }
    }
```
