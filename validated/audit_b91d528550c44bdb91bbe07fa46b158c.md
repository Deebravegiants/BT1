### Title
Missing Positivity Check Before `uint256` Cast of Chainlink `int256` Price Causes Massive Price Inflation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` casts the `int256 price` returned by Chainlink's `latestRoundData()` directly to `uint256` without first verifying `price > 0`. If the feed returns a zero or negative value, the cast silently wraps to a near-`type(uint256).max` value, inflating `totalETHInProtocol` and consequently `rsETHPrice`, causing share/asset mis-accounting across the entire protocol.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` performs:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

There is no guard on `price`. If `price == -1`, then `uint256(-1)` = `2^256 - 1 ≈ 1.16 × 10^77`, which is then multiplied by `1e18`, overflowing to a still-enormous value. This is the exact same class of bug as the reference report: a signed value that can be negative is cast to an unsigned type before any floor/max comparison, producing a massive unsigned integer instead of zero.

The sister contract `ChainlinkOracleForRSETHPoolCollateral.sol` demonstrates the correct pattern:

```solidity
if (ethPrice <= 0) revert InvalidPrice();
uint256 normalizedPrice = uint256(ethPrice) * 1e18 / ...;
``` [2](#0-1) 

`ChainlinkPriceOracle` is missing this guard entirely.

The inflated price propagates through `LRTOracle._getTotalEthInProtocol()`, which sums `totalAssetAmt.mulWad(assetER)` for every supported asset: [3](#0-2) 

This inflated `totalETHInProtocol` is then used in `_updateRsETHPrice()` to compute `newRsETHPrice`: [4](#0-3) 

### Impact Explanation
An astronomically inflated `rsETHPrice` causes every subsequent deposit to yield near-zero rsETH tokens (since `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate`). Depositors send ETH and receive essentially nothing — a direct loss of deposited funds. Simultaneously, existing rsETH holders' redemption value is distorted. This constitutes direct theft of user funds in motion (depositors) and share mis-accounting for existing holders.

**Impact: Critical** — direct theft of deposited user funds.

### Likelihood Explanation
Chainlink feeds can return zero or negative values in documented edge cases: deprecated aggregators, circuit-breaker minAnswer/maxAnswer hits, or feeds that have been sunset. The `updateRSETHPrice()` function is **public and callable by any address**: [5](#0-4) 

When `pricePercentageLimit == 0` (the default initial state before an admin sets it), the price-increase threshold check is bypassed entirely: [6](#0-5) 

This means any external caller can trigger the price update with no restriction. The condition (a Chainlink feed returning a non-positive value) is a known, documented edge case, not a theoretical one.

**Likelihood: Medium** — requires a Chainlink feed to return a non-positive value, which is an edge case but a well-documented one.

### Recommendation
Add a positivity check before casting, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    if (price <= 0) revert InvalidPrice();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

### Proof of Concept
1. A supported Chainlink feed (e.g., stETH/ETH) returns `price = -1` due to a circuit-breaker or deprecation event.
2. Any external actor calls `LRTOracle.updateRSETHPrice()`.
3. `getAssetPrice(stETH)` returns `uint256(-1) * 1e18 / 1e8` ≈ `3.4 × 10^69`.
4. `totalETHInProtocol` is set to this astronomical value.
5. `newRsETHPrice` = `3.4 × 10^69 / rsethSupply` — still an enormous number.
6. With `pricePercentageLimit == 0`, the threshold check is skipped and `rsETHPrice` is updated to this value.
7. The next user who calls `deposit()` on any pool contract receives `amountAfterFee * 1e18 / (3.4 × 10^69)` ≈ `0` rsETH, losing their entire deposit.

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L52-54)
```text
        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L32-34)
```text
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
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

**File:** contracts/LRTOracle.sol (L256-257)
```text
            bool isPriceIncreaseOffLimit =
                pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
```

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
