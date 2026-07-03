### Title
Missing Chainlink Staleness Check Allows Stale Price Acceptance for rsETH Minting — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `answer`. The `updatedAt` timestamp is never validated, meaning a stale Chainlink price feed is silently accepted and used to compute the rsETH exchange rate. This is the direct oracle-staleness analog to M-14: where M-14 describes a heartbeat that can be set too short (causing false "dead" detection and DoS), LRT-rsETH has no heartbeat check at all, causing the opposite failure — stale prices are always treated as live.

---

### Finding Description

In `ChainlinkPriceOracle.getAssetPrice()`, the call to `latestRoundData()` destructures only the `price` field:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
```

The five return values are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The `updatedAt` field (index 3) and `answeredInRound` (index 4) are both silently discarded. No comparison of `updatedAt` against `block.timestamp` is performed, and no maximum staleness threshold exists anywhere in the contract.

This price is then normalized and returned directly:

```solidity
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

`LRTOracle._getTotalEthInProtocol()` calls `getAssetPrice(asset)` for every supported LST to compute total protocol TVL, which is then used by `_updateRsETHPrice()` to set the rsETH/ETH exchange rate. The exchange rate directly governs how many rsETH tokens are minted per deposited LST. [1](#0-0) [2](#0-1) [3](#0-2) 

---

### Impact Explanation

**Temporary freezing of funds / Theft of unclaimed yield / Protocol insolvency (Medium–High)**

If a Chainlink feed for any supported LST (e.g., stETH/ETH, ETHx/ETH) goes stale — which occurs during network congestion, oracle network disruptions, or when the deviation threshold is not crossed for an extended period — the protocol continues to use the last reported price indefinitely. Two concrete harms follow:

1. **Inflated stale price (price has dropped in reality):** A depositor can deposit LSTs at the stale high price, receiving more rsETH than the actual underlying value warrants. When the oracle updates to the true lower price, existing rsETH holders are diluted — this is a form of fund theft from existing holders.

2. **Deflated stale price (price has risen in reality):** Depositors receive fewer rsETH tokens than they are entitled to, and the protocol's TVL is understated, suppressing fee accrual and distorting the `highestRsethPrice` tracker used for fee minting logic. [4](#0-3) [5](#0-4) 

---

### Likelihood Explanation

Chainlink feeds update only when the deviation threshold or heartbeat threshold is crossed. For many LST/ETH feeds, the heartbeat is 24 hours and deviation is 0.5–1%. During periods of low volatility or elevated gas prices, feeds can remain stale for hours without triggering an update. This is a well-documented, real-world occurrence (as the M-14 Dune dashboard evidence shows). Any unprivileged depositor can exploit this window simply by calling `depositAsset` or `depositETH` during a staleness period. [1](#0-0) 

---

### Recommendation

Add a staleness check in `ChainlinkPriceOracle.getAssetPrice()` using a per-asset configurable `maxStaleness` mapping (analogous to Chainlink's native heartbeat per feed). Reject prices where `block.timestamp - updatedAt > maxStaleness[asset]`. Also validate `answeredInRound >= roundId` and `price > 0`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();

require(price > 0, "Invalid price");
require(answeredInRound >= roundId, "Stale round");
require(block.timestamp - updatedAt <= maxStaleness[asset], "Stale price");
``` [1](#0-0) 

---

### Proof of Concept

**Attacker-controlled entry path:**

1. Monitor the Chainlink feed for a supported LST (e.g., stETH/ETH at `0x86392dC19c0b719886221c78AB11eb8Cf5c52812`).
2. Wait for the feed to go stale — e.g., during a period of low volatility where the price has not moved enough to trigger the deviation threshold, but the actual market price has dropped 2–3%.
3. Call `LRTDepositPool.depositAsset(stETH, largeAmount, minRSETH, "")` — this is a public, permissionless function.
4. `LRTOracle.getRsETHAmountToMint()` calls `getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → `latestRoundData()` returns the stale (inflated) price with no rejection.
5. The depositor receives rsETH computed at the stale high price, more than the true underlying value.
6. When the oracle next updates to the true lower price, the depositor's rsETH is worth more than what they deposited, at the expense of existing rsETH holders. [1](#0-0) [6](#0-5)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L244-250)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L294-296)
```text
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
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
