### Title
Stale Chainlink Spot Price Accepted Without Staleness Validation Enables Favorable rsETH Minting Rate Exploitation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` and uses the returned price without validating the `updatedAt` timestamp. When a Chainlink LST/ETH feed goes stale at a price below the true market rate, an unprivileged depositor can call the public `LRTOracle.updateRSETHPrice()` to deflate the stored `rsETHPrice`, then deposit ETH to receive more rsETH than the protocol's actual NAV justifies, diluting existing rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the latest Chainlink round without any staleness guard:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

The `updatedAt` field returned by `latestRoundData` is silently discarded. No heartbeat or maximum-age check is applied.

This price is consumed by `LRTOracle._getTotalEthInProtocol()`, which iterates every supported LST and multiplies its balance by the Chainlink spot price to compute total protocol ETH value:

```solidity
uint256 assetER = getAssetPrice(asset);
uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [2](#0-1) 

`_getTotalEthInProtocol()` feeds directly into `_updateRsETHPrice()`, which computes and stores the new `rsETHPrice`:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [3](#0-2) 

`updateRSETHPrice()` is a public, permissionless function callable by anyone:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [4](#0-3) 

The stored `rsETHPrice` is then used as the denominator when computing how many rsETH tokens to mint per deposited asset:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [5](#0-4) 

---

### Impact Explanation

When a Chainlink LST/ETH feed (e.g., stETH/ETH) goes stale at a price **below** the true market rate, the computed `totalETHInProtocol` is understated, causing `rsETHPrice` to be deflated. A depositor who then sends native ETH (whose value is always treated as exactly `1e18`, bypassing any oracle) receives:

```
rsETHAmountToMint = (ethAmount * 1e18) / deflatedRsETHPrice
```

This yields more rsETH than the depositor's ETH is actually worth relative to the protocol's true NAV. When prices normalize and `rsETHPrice` recovers, the attacker's rsETH redeems for more ETH than was deposited, extracting value from existing rsETH holders. This constitutes **theft of unclaimed yield** (High) from existing holders.

The downside-protection threshold (`pricePercentageLimit`) provides partial mitigation only if it is set and the price deviation exceeds it; if `pricePercentageLimit == 0` (its default after `initialize`) or the deviation is within the limit, the deflated price is accepted and the protocol is not paused. [6](#0-5) 

---

### Likelihood Explanation

Chainlink feeds have documented periods of staleness during Ethereum network congestion, gas price spikes, or oracle node downtime. The attacker does not need to cause the staleness — they only need to observe it (e.g., by monitoring `updatedAt` on-chain) and act within the stale window. The entry path (`updateRSETHPrice()` + `depositETH()`) is fully permissionless and requires no special role. Likelihood is **Medium**.

---

### Recommendation

Add a staleness check in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
require(block.timestamp - updatedAt <= MAX_STALENESS, "Stale price");
```

`MAX_STALENESS` should be set per-feed based on the Chainlink heartbeat (e.g., 3600 seconds for most ETH-denominated feeds). Additionally, validate that `price > 0` to guard against invalid rounds.

---

### Proof of Concept

1. Protocol holds 1000 stETH (true market rate: 0.99 ETH/stETH) and 0 ETH. rsETH supply = 990. True rsETHPrice ≈ 1.0 ETH/rsETH.
2. Chainlink stETH/ETH feed goes stale at 0.90 ETH/stETH (below actual).
3. Attacker calls `LRTOracle.updateRSETHPrice()`:
   - `_getTotalEthInProtocol()` = 1000 × 0.90 = 900 ETH (stale, understated)
   - `newRsETHPrice` = 900 / 990 ≈ 0.909 ETH/rsETH (deflated)
   - Price drop = (1.0 − 0.909)/1.0 = 9.1%. If `pricePercentageLimit` is 0 or > 9.1%, update succeeds.
4. Attacker calls `LRTDepositPool.depositETH{value: 10 ether}("")`:
   - `rsethAmountToMint` = (10 × 1e18) / 0.909e18 ≈ **11.0 rsETH**
5. Chainlink feed updates; `updateRSETHPrice()` is called again:
   - `_getTotalEthInProtocol()` = 1000 × 0.99 + 10 = 1000 ETH
   - rsETH supply = 990 + 11 = 1001
   - `newRsETHPrice` = 1000 / 1001 ≈ 0.999 ETH/rsETH
6. Attacker redeems 11.0 rsETH → receives ≈ 10.99 ETH.
7. **Net profit ≈ 0.99 ETH** on a 10 ETH deposit, extracted from existing holders. [1](#0-0) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L270-281)
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

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```
