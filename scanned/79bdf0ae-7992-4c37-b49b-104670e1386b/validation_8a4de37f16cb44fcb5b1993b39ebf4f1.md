### Title
Stale/Zero Chainlink Price for Any Single Supported Asset Triggers Protocol-Wide Auto-Pause, Freezing All Deposits and Withdrawals — (File: `contracts/oracles/ChainlinkPriceOracle.sol`, `contracts/LRTOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` fetches `latestRoundData()` but discards every validity field (`updatedAt`, `answeredInRound`, `roundId`), accepting any price including 0. `LRTOracle._getTotalEthInProtocol()` iterates over **all** supported assets and calls this unchecked oracle for each. If any single Chainlink feed returns a stale or zero price, the computed `totalETHInProtocol` collapses, `newRsETHPrice` drops far below `highestRsethPrice`, and the built-in downside-protection logic in `_updateRsETHPrice()` auto-pauses the deposit pool, withdrawal manager, and oracle — freezing all user operations. `updateRSETHPrice()` is public, so any unprivileged caller can trigger this path.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads only the `answer` field from `latestRoundData()`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
``` [1](#0-0) 

`updatedAt`, `answeredInRound`, and `roundId` are all silently discarded. A stale round, an incomplete round, or a zero/negative answer all pass through without revert.

By contrast, the pool-level oracle wrapper `ChainlinkOracleForRSETHPoolCollateral` correctly validates all three conditions:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L26-37
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

The unchecked oracle feeds directly into `_getTotalEthInProtocol()`, which loops over **every** supported asset:

```solidity
// contracts/LRTOracle.sol L331-349
for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
    address asset = supportedAssets[assetIdx];
    uint256 assetER = getAssetPrice(asset);          // ← no staleness guard
    uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);
    totalETHInProtocol += totalAssetAmt.mulWad(assetER);
    ...
}
``` [3](#0-2) 

If `assetER` is 0 for any asset, that asset's entire TVL contribution is erased from `totalETHInProtocol`. `_updateRsETHPrice()` then computes a `newRsETHPrice` far below `highestRsethPrice` and executes the auto-pause branch:

```solidity
// contracts/LRTOracle.sol L270-282
if (isPriceDecreaseOffLimit) {
    if (!lrtDepositPool.paused()) lrtDepositPool.pause();
    if (!withdrawalManager.paused()) withdrawalManager.pause();
    _pause();
    return;
}
``` [4](#0-3) 

`updateRSETHPrice()` is unrestricted:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
``` [5](#0-4) 

Any address can call it, including a bot or a user who notices a stale feed.

---

### Impact Explanation

When the auto-pause fires, `LRTDepositPool.pause()` and `LRTWithdrawalManager.pause()` are both called, blocking `depositETH`, `depositAsset`, and all withdrawal operations for every user of the protocol — regardless of which asset's oracle was stale. Recovery requires manual admin intervention to unpause each contract. This constitutes **temporary freezing of funds** across the entire protocol.

---

### Likelihood Explanation

Chainlink feeds can return stale or zero data during: heartbeat misses under network congestion, feed deprecation/migration, circuit-breaker events, or sequencer downtime on L2. The protocol supports multiple LST assets (stETH, ETHx, etc.), each with its own feed. The probability that at least one feed experiences a transient anomaly over the protocol's lifetime is non-trivial. Because `updateRSETHPrice()` is public and callable by anyone, no privileged access is needed to trigger the pause — a keeper bot or any observer can do it the moment a feed goes stale.

---

### Recommendation

1. Add staleness and validity checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
require(answeredInRound >= roundId, "Stale price");
require(updatedAt > 0, "Incomplete round");
require(price > 0, "Invalid price");
```

2. In `_getTotalEthInProtocol()`, consider skipping assets whose oracle is temporarily unavailable (returning a cached or last-known price) rather than allowing a single bad feed to corrupt the aggregate TVL and trigger a system-wide pause.

3. Decouple the auto-pause trigger from oracle-computed TVL so that a feed anomaly does not automatically freeze user funds without additional circuit-breaker logic.

---

### Proof of Concept

1. Protocol has two supported assets: ETH and stETH. `pricePercentageLimit` is set to `1e16` (1%).
2. The stETH Chainlink feed (`stETH/ETH`) experiences a heartbeat miss and `latestRoundData()` returns `answeredInRound < roundId` with `price = 0`.
3. `ChainlinkPriceOracle.getAssetPrice(stETH)` returns `0` — no revert, no check.
4. `_getTotalEthInProtocol()` computes `totalETHInProtocol` as if all stETH TVL is worth 0 ETH.
5. `newRsETHPrice = (totalETHInProtocol - 0) / rsethSupply` is, say, 0.5 ETH while `highestRsethPrice` is 1.05 ETH.
6. `diff = 0.55 ETH > pricePercentageLimit.mulWad(highestRsethPrice) = 0.0105 ETH` → `isPriceDecreaseOffLimit = true`.
7. Any user (or bot) calls `updateRSETHPrice()`.
8. `lrtDepositPool.pause()`, `withdrawalManager.pause()`, `_pause()` execute.
9. All deposits and withdrawals revert with `Pausable: paused` until admin manually unpauses — **temporary protocol-wide freeze**. [1](#0-0) [6](#0-5) [4](#0-3)

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

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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
