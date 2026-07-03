### Title
Missing Chainlink Price Feed Staleness Validation Allows Stale Prices to Corrupt rsETH Rate Computation - (`contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `price`, performing no staleness validation. A stale Chainlink feed silently returns an outdated price, which propagates into `LRTOracle._updateRsETHPrice()` and corrupts the rsETH/ETH exchange rate used for deposits, withdrawals, and fee minting.

---

### Finding Description

In `contracts/oracles/ChainlinkPriceOracle.sol`, `getAssetPrice()` fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The contract discards `roundId`, `startedAt`, `updatedAt`, and `answeredInRound` entirely. There is no check that:
- `updatedAt` is within an acceptable heartbeat window (e.g., `block.timestamp - updatedAt < MAX_DELAY`)
- `answeredInRound >= roundId` (round completeness)
- `price > 0` (non-negative price)

This oracle is registered in `LRTOracle` as the price source for supported LST assets (stETH, rETH, etc.):

```solidity
function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
    return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
}
``` [2](#0-1) 

`getAssetPrice()` is called inside `_updateRsETHPrice()` → `_getTotalEthInProtocol()`, which computes the total ETH backing rsETH and derives the rsETH/ETH exchange rate stored in `rsETHPrice`. [3](#0-2) 

---

### Impact Explanation

A stale LST price (e.g., during a Chainlink node outage or network congestion) will silently produce an incorrect `totalETHInProtocol` value. Two concrete consequences:

1. **Incorrect rsETH price**: If the stale price is lower than the true price, `newRsETHPrice` is understated. If the deviation exceeds `pricePercentageLimit`, the downside-protection logic at lines 270–281 triggers an automatic pause of `LRTDepositPool` and `LRTWithdrawalManager`, **temporarily freezing all user deposits and withdrawals** without any actual loss event. [4](#0-3) 

2. **Incorrect fee minting**: If the stale price is higher than the true price, `totalETHInProtocol > previousTVL` is falsely satisfied, causing unearned protocol fees to be minted as rsETH, diluting existing holders. [5](#0-4) 

Impact classification: **Medium — Temporary freezing of funds** (scenario 1) and **High — Theft of unclaimed yield** (scenario 2).

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 1 hour for ETH/stETH). During periods of low volatility, feeds may not update for the full heartbeat window. On mainnet, extended outages are rare but have occurred. The `updateRSETHPrice()` function is public and callable by anyone, meaning any caller can trigger the stale-price path at any time without special access. [6](#0-5) 

---

### Recommendation

Add staleness and validity checks in `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    require(price > 0, "Invalid price");
    require(answeredInRound >= roundId, "Stale round");
    require(block.timestamp - updatedAt <= MAX_STALENESS_DELAY, "Stale price");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`MAX_STALENESS_DELAY` should be set per-feed based on the Chainlink heartbeat (e.g., 3600 seconds for 1-hour feeds, with a small buffer).

---

### Proof of Concept

1. Chainlink's stETH/ETH feed stops updating (e.g., heartbeat window expires during low volatility).
2. Any address calls `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_updateRsETHPrice()` calls `_getTotalEthInProtocol()`, which calls `ChainlinkPriceOracle.getAssetPrice(stETH)`.
4. `getAssetPrice` calls `priceFeed.latestRoundData()` and returns the stale (lower) price without reverting.
5. `totalETHInProtocol` is understated; `newRsETHPrice` falls below `highestRsethPrice` by more than `pricePercentageLimit`.
6. The contract executes `lrtDepositPool.pause()`, `withdrawalManager.pause()`, and `_pause()` — all user deposits and withdrawals are frozen. [7](#0-6) [8](#0-7)

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

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
```

**File:** contracts/LRTOracle.sol (L214-231)
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

**File:** contracts/LRTOracle.sol (L244-247)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L270-282)
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
            }
```
