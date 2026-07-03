### Title
Lack of price freshness check in `ChainlinkPriceOracle.sol#getAssetPrice()` allows stale Chainlink price to be used for rsETH minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all staleness-related return values (`updatedAt`, `answeredInRound`, `roundId`). A stale inflated price for any supported LST asset allows an unprivileged depositor to mint more rsETH than the real ETH value of their deposit, diluting all existing rsETH holders.

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows: [1](#0-0) 

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The implementation silently discards `roundId`, `startedAt`, `updatedAt`, and `answeredInRound`. There is no check of the form:

- `block.timestamp - updatedAt <= heartbeat` (time-based freshness)
- `answeredInRound >= roundId` (round-completeness / deprecated-round guard)
- `price > 0` (negative/zero price guard)

By contrast, the sibling contract `ChainlinkOracleForRSETHPoolCollateral.sol` in the same repository does perform partial staleness checks: [2](#0-1) 

This inconsistency confirms the team is aware of the requirement but omitted it from the primary deposit-path oracle.

### Impact Explanation

The stale price flows directly into rsETH minting: [3](#0-2) 

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.getAssetPrice(asset)` delegates to `ChainlinkPriceOracle.getAssetPrice()`: [4](#0-3) 

If the Chainlink feed for a supported LST (e.g., stETH/ETH, rETH/ETH) is stale and its last reported price is higher than the current market price (e.g., during a flash crash or Chainlink node outage), a depositor receives more rsETH than the real ETH value of their deposit. When they later redeem, they extract more ETH than they contributed, directly stealing value from all other rsETH holders. This constitutes **theft of user funds / protocol insolvency**.

The `pricePercentageLimit` guard in `_updateRsETHPrice` does not protect against this: it only gates the rsETH price *update* transaction, not individual `getAssetPrice` calls made during deposits. [5](#0-4) 

### Likelihood Explanation

Chainlink feeds do not stream data continuously. They update only when price deviation exceeds a threshold or the heartbeat idle time elapses (typically 1 hour on mainnet, up to 24 hours for some feeds). During periods of network congestion, Chainlink node issues, or rapid market moves ("flash crashes"), the on-chain price can lag the real market price for the full heartbeat window. This is a well-documented, realistic scenario — not a theoretical edge case.

Any unprivileged user can call `depositAsset()` at any time, so no special access is required to exploit the window.

### Recommendation

Add staleness and validity checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price, , uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    // heartbeat should be configurable per feed (e.g., 1 hour for most ETH mainnet feeds)
    if (block.timestamp - updatedAt > feedHeartbeat[asset]) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Store a `mapping(address asset => uint256 heartbeat) public feedHeartbeat` and require it to be set alongside `assetPriceFeed` in `updatePriceFeedFor`.

### Proof of Concept

1. Assume stETH/ETH Chainlink feed last updated at `T-2h` with price `1.05 ETH` (heartbeat = 1 h).
2. At `T`, the real market price of stETH drops to `0.90 ETH` (flash crash), but the feed is not yet updated.
3. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
4. `getRsETHAmountToMint` computes: `rsethToMint = 1000e18 * 1.05e18 / rsETHPrice` — inflated by ~16.7%.
5. Attacker receives ~167 extra rsETH relative to the real value deposited.
6. Once the feed updates and `rsETHPrice` is recalculated to reflect the true lower stETH value, the attacker redeems their rsETH and extracts more ETH than they deposited, at the expense of all other rsETH holders. [1](#0-0) [6](#0-5)

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

**File:** contracts/LRTDepositPool.sol (L506-521)
```text
    function getRsETHAmountToMint(
        address asset,
        uint256 amount
    )
        public
        view
        override
        returns (uint256 rsethAmountToMint)
    {
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
    }
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
