### Title
`ChainlinkPriceOracle.getAssetPrice()` Accepts Stale/Invalid Chainlink Data With No Fallback, Freezing Deposits and Withdrawals — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls Chainlink's `latestRoundData()` but performs **no validation** of the returned values (no staleness check, no zero/negative price guard). `LRTOracle.getAssetPrice()` delegates directly to this oracle with no try-catch and no fallback oracle. If the Chainlink feed returns a non-positive price, the implicit `uint256(price)` cast reverts in Solidity 0.8+, and that revert propagates uncaught through `LRTOracle` into every critical protocol path: deposits, withdrawals, and rsETH price updates.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

There is no check on:
- `answeredInRound >= roundId` (stale round detection)
- `updatedAt != 0` (incomplete round detection)
- `price > 0` (valid price guard)

If `price` is zero or negative (possible during Chainlink circuit-breaker events or feed deprecation), the Solidity 0.8 checked arithmetic causes `uint256(price)` to revert when `price < 0`. Even when `price == 0`, the function returns `0`, which is silently accepted.

`LRTOracle.getAssetPrice()` delegates to this oracle with no try-catch and no fallback:

```solidity
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [2](#0-1) 

`_getTotalEthInProtocol()` calls `getAssetPrice()` for every supported asset in a loop:

```solidity
uint256 assetER = getAssetPrice(asset);
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [3](#0-2) 

A revert in any single asset's oracle propagates out of `_updateRsETHPrice()` entirely, blocking the rsETH price update. Separately, `LRTDepositPool.getRsETHAmountToMint()` and `LRTWithdrawalManager._createUnlockParams()` both call `lrtOracle.getAssetPrice()` directly:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [4](#0-3) 

```solidity
assetPrice: lrtOracle.getAssetPrice(asset),
``` [5](#0-4) 

Neither call is wrapped in a try-catch, and no fallback oracle exists anywhere in the system.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

If any supported asset's Chainlink feed enters a state where `latestRoundData()` reverts or returns `price <= 0`:

1. `depositAsset()` / `depositETH()` revert — users cannot deposit.
2. `unlockQueue()` in `LRTWithdrawalManager` reverts — pending withdrawal requests cannot be processed, temporarily freezing user funds in the queue.
3. `updateRSETHPrice()` reverts — the rsETH exchange rate cannot be updated, stalling the protocol's accounting.

The freeze persists until the Chainlink feed recovers or an admin manually swaps the price oracle — there is no automatic fallback path.

---

### Likelihood Explanation

Chainlink feeds can return `price = 0` or revert during:
- Feed deprecation / migration to a new aggregator address
- L2 sequencer downtime (if the protocol is deployed on L2)
- Extreme market conditions triggering Chainlink's circuit-breaker (min/max answer bounds)

These are documented, real-world Chainlink failure modes. The protocol supports multiple LST assets (stETH, rETH, ETHx, sfrxETH, swETH), each with its own Chainlink feed, so the attack surface is multiplied. A single feed failure is sufficient to freeze the entire deposit/withdrawal flow.

---

### Recommendation

1. **Validate `latestRoundData()` return values** in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Stale price");
require(updatedAt != 0, "Incomplete round");
require(price > 0, "Invalid price");
```

2. **Add a fallback oracle** in `LRTOracle.getAssetPrice()` using try-catch, so that if the primary oracle reverts, a secondary source (e.g., a TWAP or protocol-internal rate) is consulted before reverting to callers.

3. **Guard `_getTotalEthInProtocol()`** with per-asset try-catch so that a single oracle failure does not block the entire rsETH price update.

---

### Proof of Concept

1. Chainlink's `stETH/ETH` feed is deprecated and begins reverting on `latestRoundData()`.
2. Any user calls `depositAsset(stETH, amount, minRSETH, "")`.
3. `_beforeDeposit()` → `getRsETHAmountToMint()` → `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → `priceFeed.latestRoundData()` **reverts**.
4. The revert propagates with no try-catch at any layer; the deposit fails.
5. Simultaneously, `unlockQueue()` in `LRTWithdrawalManager` also reverts for the same reason, freezing all pending stETH withdrawal requests.
6. No fallback oracle is consulted at any point. [1](#0-0) [2](#0-1) [6](#0-5)

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

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTWithdrawalManager.sol (L848-848)
```text
            assetPrice: lrtOracle.getAssetPrice(asset),
```
