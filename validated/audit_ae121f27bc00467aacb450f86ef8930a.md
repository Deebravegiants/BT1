### Title
Chainlink Price Oracle Lacks Staleness Validation, Allowing a Single Stale Feed to Manipulate rsETH Minting Rate — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards the `updatedAt` and `answeredInRound` return values, performing no staleness check. A single Chainlink feed that goes stale (returns an old, lower price) causes `LRTOracle._getTotalEthInProtocol()` to underestimate the protocol's total ETH value, which lowers the stored `rsETHPrice`. An unprivileged attacker can then call the public `updateRSETHPrice()` to lock in the stale price and immediately deposit ETH to mint excess rsETH at the expense of existing holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

The destructured return values `updatedAt` and `answeredInRound` are silently ignored. [1](#0-0) 

This price is consumed by `LRTOracle._getTotalEthInProtocol()`, which sums `totalAssetAmt * assetER` across all supported LSTs to compute the protocol's total ETH value. [2](#0-1) 

That total is then used to compute and store `rsETHPrice`:

```solidity
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
``` [3](#0-2) 

`updateRSETHPrice()` is `public` and callable by anyone:

```solidity
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [4](#0-3) 

The stored `rsETHPrice` directly controls how much rsETH a depositor receives:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [5](#0-4) 

The same stale-price path is present in `RSETHPoolV3.viewSwapRsETHAmountAndFee()` on L2, which calls `getRate()` on the `CrossChainRateReceiver` — itself populated from the stale L1 price — to compute wrsETH minting amounts. [6](#0-5) 

---

### Impact Explanation

If a Chainlink feed for a large LST (e.g., stETH/ETH or ETHx/ETH) goes stale and returns a price lower than the real market price:

1. `_getTotalEthInProtocol()` underestimates the protocol's total ETH value.
2. `rsETHPrice` is set below its fair value.
3. An attacker deposits ETH (priced at the fixed `1e18` via `OneETHPriceOracle`) and receives more rsETH than the fair exchange rate entitles them to.
4. When the Chainlink feed recovers and `rsETHPrice` is corrected upward, the attacker's excess rsETH is worth more than they paid — the difference is extracted from existing rsETH holders.

The `pricePercentageLimit` guard only triggers a pause when the price deviation exceeds the configured threshold. If `pricePercentageLimit == 0` (unset), there is no protection at all. Even when set, deviations within the limit (e.g., 1–3% staleness) are silently accepted and fully exploitable. [7](#0-6) 

**Impact: High — Theft of unclaimed yield / dilution of existing rsETH holders.**

---

### Likelihood Explanation

Chainlink feeds can go stale without any oracle operator compromise: network congestion, gas price spikes, or heartbeat gaps are well-documented real-world events. The attacker does not need to compromise any key or role — they only need to observe a stale feed and call the public `updateRSETHPrice()` before the feed recovers. This is a passive, low-cost, permissionless exploit path.

---

### Recommendation

Add staleness and sanity validation in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound)
    = priceFeed.latestRoundData();

require(price > 0, "Invalid price");
require(answeredInRound >= roundId, "Stale round");
require(block.timestamp - updatedAt <= MAX_STALENESS, "Stale price");
```

`MAX_STALENESS` should be set per-feed based on the feed's documented heartbeat (e.g., 3600 seconds for a 1-hour heartbeat feed). Additionally, consider adding a deviation circuit-breaker in `_updateRsETHPrice()` that compares the new price against a secondary on-chain source (e.g., the LST protocol's own exchange rate) before committing it.

---

### Proof of Concept

1. Chainlink stETH/ETH feed goes stale, returning a price 5% below the real rate (e.g., due to network congestion).
2. Attacker calls `LRTOracle.updateRSETHPrice()` (public, no access control). `rsETHPrice` is now 5% below fair value.
3. Attacker calls `LRTDepositPool.depositETH{value: 1000 ether}(0, "")`. Because `rsETHPrice` is 5% low, `rsethAmountToMint = 1000e18 * 1e18 / rsETHPrice` yields ~1052 rsETH instead of the fair ~1000 rsETH.
4. Chainlink feed recovers. A legitimate keeper calls `updateRSETHPrice()` again; `rsETHPrice` returns to fair value.
5. Attacker holds ~52 rsETH of excess value extracted from existing holders, redeemable at the corrected rate.

The root cause — the missing staleness check — is entirely within the protocol's own code at: [8](#0-7)

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

**File:** contracts/LRTOracle.sol (L252-267)
```text
        if (newRsETHPrice > highestRsethPrice) {
            // check if the price is above the threshold
            uint256 priceDifference = newRsETHPrice - highestRsethPrice;
            // pricePercentageLimit is in 1e18 precision (100% = 1e18, 1% = 1e16)
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);

            // check if the price difference is above the threshold
            if (isPriceIncreaseOffLimit) {
                // if sender has a manager role, this doesn't revert.
                // if not, it reverts as price went above the threshold
                if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
                    revert PriceAboveDailyThreshold();
                }
            }
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

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-307)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
