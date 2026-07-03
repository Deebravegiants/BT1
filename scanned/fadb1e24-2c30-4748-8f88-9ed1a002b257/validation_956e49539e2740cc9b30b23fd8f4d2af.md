### Title
Missing Chainlink Oracle Staleness Check Allows Stale Price Consumption - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but completely discards the `updatedAt` timestamp, performing no heartbeat or staleness validation. This is the direct analog of M-12: instead of using the same heartbeat for two feeds, the contract uses **no heartbeat check at all** for any feed.

---

### Finding Description

In `contracts/oracles/ChainlinkPriceOracle.sol`, the `getAssetPrice()` function fetches the Chainlink price but silently ignores the `updatedAt` return value:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The contract binds only `price` (the second slot) and discards all others, including `updatedAt`. No comparison against a maximum staleness threshold (heartbeat) is ever performed.

This oracle is registered per-asset in `LRTOracle.assetPriceOracle` and is called during `_updateRsETHPrice()` via `_getTotalEthInProtocol()` → `getAssetPrice()`. [2](#0-1) 

Different Chainlink feeds have different heartbeats (e.g., stETH/ETH is 24 h on mainnet, cbETH/ETH is 24 h, ETH/USD is 1 h). With no staleness check, a feed that has stopped updating will silently supply its last known price indefinitely.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns.**

If one or more Chainlink feeds go stale (e.g., during network congestion, a Chainlink node outage, or a feed deprecation), `_updateRsETHPrice()` will compute an incorrect `totalETHInProtocol` using the last cached price. The resulting `rsETHPrice` will be wrong:

- If the stale price is **lower** than the true price, depositors receive **more rsETH** than they are entitled to, diluting existing holders.
- If the stale price is **higher** than the true price, depositors receive **fewer rsETH** than they are entitled to, causing a direct loss to the depositor.

The `pricePercentageLimit` guard in `LRTOracle` only triggers on large single-step price jumps; a gradually stale feed that drifts slowly will pass through undetected. [3](#0-2) 

---

### Likelihood Explanation

Chainlink feeds do occasionally miss heartbeat windows during L1/L2 congestion or sequencer downtime. The affected assets (stETH, cbETH, ETHx, etc.) all have 24-hour heartbeats, meaning a feed can be up to 24 hours stale before Chainlink's own circuit-breaker would fire — and the protocol would never detect it.

---

### Recommendation

Add a per-feed maximum staleness parameter and validate `updatedAt` in `getAssetPrice()`:

```solidity
mapping(address asset => uint256 maxStaleness) public assetMaxStaleness;

function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,, uint256 updatedAt,) = priceFeed.latestRoundData();
    require(block.timestamp - updatedAt <= assetMaxStaleness[asset], "Stale price");
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Each asset's `maxStaleness` should be set to match the Chainlink heartbeat for that specific feed (e.g., 86 400 s for 24 h feeds, 3 600 s for 1 h feeds), mirroring the fix applied in the referenced M-12 commits.

---

### Proof of Concept

1. Chainlink's stETH/ETH feed stops updating (e.g., sequencer downtime on Arbitrum, or a node outage).
2. The last reported price was `1.05 ETH` per stETH; the true market price has moved to `1.00 ETH`.
3. Any caller invokes `LRTOracle.updateRSETHPrice()` (public, no access control).
4. `_getTotalEthInProtocol()` calls `ChainlinkPriceOracle.getAssetPrice(stETH)`.
5. `latestRoundData()` returns the stale `1.05` price; `updatedAt` is ignored.
6. `totalETHInProtocol` is overstated by ~5%, inflating `rsETHPrice`.
7. A depositor mints rsETH at the inflated rate, receiving fewer tokens than deserved; or an attacker who observed the staleness deposits ETH and redeems at the inflated rsETH price, extracting value from existing holders. [4](#0-3) [5](#0-4)

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

**File:** contracts/LRTOracle.sol (L214-232)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

```

**File:** contracts/LRTOracle.sol (L252-266)
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
```
