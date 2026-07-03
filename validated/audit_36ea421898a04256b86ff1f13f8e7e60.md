### Title
Chainlink `latestRoundData()` Return Values Not Validated for Staleness or Round Completeness - (`contracts/oracles/ChainlinkPriceOracle.sol`)

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all return values except `price`, performing no staleness check (`answeredInRound >= roundId`), no incomplete-round check (`updatedAt > 0`), and no non-negative price check. A stale or zero price propagates directly into rsETH minting calculations and the rsETH price update mechanism.

### Finding Description

In `contracts/oracles/ChainlinkPriceOracle.sol`, `getAssetPrice()` fetches the Chainlink price as:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

The `roundId`, `updatedAt`, and `answeredInRound` return values are all silently discarded. No checks are performed for:
- `price > 0` (zero price returns silently as 0)
- `answeredInRound >= roundId` (stale round detection)
- `updatedAt > 0` (incomplete round detection)

By contrast, `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol` — another oracle wrapper in the same repository — correctly validates all three conditions:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

This inconsistency confirms the missing validation in `ChainlinkPriceOracle` is an oversight, not a design choice.

### Impact Explanation

`ChainlinkPriceOracle.getAssetPrice()` feeds into two critical paths:

**Path 1 — rsETH price update (`updateRSETHPrice`):**
`LRTOracle._getTotalEthInProtocol()` calls `getAssetPrice(asset)` for every supported asset and multiplies by total deposits to compute total ETH in the protocol. [3](#0-2) 

A stale or zero price for any asset causes `totalETHInProtocol` to be understated. This feeds into `newRsETHPrice` computation: [4](#0-3) 

If the understatement is large enough, the downside-protection logic triggers and pauses `LRTDepositPool` and `WithdrawalManager`, temporarily freezing all user funds: [5](#0-4) 

**Path 2 — rsETH minting (`depositAsset` / `depositETH`):**
`LRTDepositPool.getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(asset)` to determine how many rsETH tokens to mint per unit of deposited asset: [6](#0-5) 

A stale price (higher or lower than actual) causes depositors to receive an incorrect rsETH amount — either over-minting (diluting existing holders) or under-minting (loss to the depositor).

**Impact classification:** Medium — temporary freezing of funds (false pause triggered by stale zero price) and contract failing to deliver promised returns (incorrect rsETH minting ratio).

### Likelihood Explanation

Chainlink feeds can return stale data during network congestion, oracle node downtime, or when a feed is deprecated. The `answeredInRound < roundId` condition is a documented Chainlink staleness indicator. This is a well-known class of vulnerability with real historical occurrences. Any public caller of `updateRSETHPrice()` or `depositAsset()` / `depositETH()` can trigger the vulnerable path without any special privileges.

### Recommendation

Apply the same validation pattern already used in `ChainlinkOracleForRSETHPoolCollateral.sol` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    require(price > 0, "ChainlinkPriceOracle: price <= 0");
    require(answeredInRound >= roundId, "ChainlinkPriceOracle: stale price");
    require(updatedAt > 0, "ChainlinkPriceOracle: incomplete round");

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, consider adding a `heartbeat`-based freshness check (e.g., `block.timestamp - updatedAt <= MAX_DELAY`) per feed.

### Proof of Concept

1. Chainlink's ETH/stETH feed (or any supported asset feed) enters a stale round — `answeredInRound < roundId` — and returns `price = 0` or a significantly outdated price.
2. Any user (or a keeper bot) calls `LRTOracle.updateRSETHPrice()` (public, no access control).
3. `_updateRsETHPrice()` → `_getTotalEthInProtocol()` → `getAssetPrice(asset)` → `ChainlinkPriceOracle.getAssetPrice()` returns 0 for the stale asset.
4. `totalETHInProtocol` is understated; `newRsETHPrice` drops below `highestRsethPrice` by more than `pricePercentageLimit`.
5. The protocol auto-pauses: `LRTDepositPool.pause()` and `WithdrawalManager.pause()` are called — all deposits and withdrawals are frozen until an admin manually unpauses.

Alternatively, if the stale price is non-zero but outdated (e.g., 10% above actual), a depositor calling `depositAsset()` receives 10% more rsETH than they should, diluting all existing rsETH holders. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L30-32)
```text
        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();
```

**File:** contracts/LRTOracle.sol (L87-88)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L277-281)
```text
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
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

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
