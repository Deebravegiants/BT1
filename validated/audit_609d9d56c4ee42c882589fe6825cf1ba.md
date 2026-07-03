### Title
Stale Chainlink Price Accepted in `ChainlinkPriceOracle` Enables Over-Minting of rsETH During Sudden LST Price Drops - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards the `updatedAt` timestamp and `answeredInRound` fields, accepting arbitrarily stale prices with no staleness validation. During sudden LST depeg or price-drop events — exactly when Chainlink feeds are most likely to lag — an unprivileged depositor can exploit the inflated stale price to mint more rsETH than their deposit is worth, diluting all existing rsETH holders.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

The five return values of `latestRoundData()` are `(roundId, answer, startedAt, updatedAt, answeredInRound)`. The code destructures only `price` (`answer`) and silently ignores `updatedAt` and `answeredInRound`. No check is made that:
- `answeredInRound >= roundId` (round completeness / sequencer liveness)
- `block.timestamp - updatedAt <= maxStaleness` (freshness)

The protocol's own pool-level oracle wrapper already performs both checks:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L27-32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();

if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

`ChainlinkPriceOracle` is the oracle adapter used by `LRTOracle.getAssetPrice()`, which is called inside `LRTOracle._getTotalEthInProtocol()` (to compute `rsETHPrice`) and directly by `LRTDepositPool.getRsETHAmountToMint()` at deposit time:

```solidity
// contracts/LRTDepositPool.sol L519-520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

### Impact Explanation
During a sudden LST depeg or price crash (e.g., stETH, rETH, ETH-X), Chainlink feeds can lag behind the real market price — especially during Ethereum network congestion when keeper transactions are delayed. While the feed is stale and still reporting the old (higher) price, any depositor can:

1. Deposit the depegged LST at the stale inflated exchange rate.
2. Receive more rsETH than the true ETH value of their deposit.
3. Redeem or sell the excess rsETH, extracting value from all existing rsETH holders.

Because `rsETHPrice` is a stored state variable updated by a separate `updateRSETHPrice()` call, the stale asset price feeds directly into the mint ratio without any on-chain freshness gate. The dilution is permanent once the feed corrects and `rsETHPrice` is updated downward.

**Impact: High — Theft of unclaimed yield / share mis-accounting that permanently dilutes existing rsETH holders.**

### Likelihood Explanation
Chainlink feeds have documented heartbeat intervals (e.g., 1 hour for stETH/ETH on mainnet). During extreme market events — precisely when LST prices move sharply — network congestion delays keeper updates, and feeds can remain stale for multiple heartbeat periods. The external report's scenario (sudden extreme price variation + network congestion) maps directly to this code path. The attack requires no special role; any depositor can execute it permissionlessly via `depositAsset()` or `depositETH()`.

**Likelihood: Medium.**

### Recommendation
Apply the same staleness and round-completeness checks already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`MAX_STALENESS` should be set per-asset to slightly exceed the Chainlink heartbeat for that feed.

### Proof of Concept

**Setup:** stETH/ETH Chainlink feed heartbeat = 1 hour. A depeg event occurs; stETH real price drops to 0.90 ETH. Network congestion delays the Chainlink keeper; the feed still reports 1.00 ETH (stale).

**Attack steps:**

1. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
2. `_beforeDeposit` → `getRsETHAmountToMint(stETH, 1000e18)`.
3. `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns `1.00e18` (stale).
4. Suppose `rsETHPrice = 1.05e18`. Minted rsETH = `1000e18 * 1.00e18 / 1.05e18 ≈ 952.38 rsETH`.
5. True value of 1000 stETH = 900 ETH → fair rsETH = `900e18 / 1.05e18 ≈ 857.14 rsETH`.
6. Attacker receives **≈ 95 excess rsETH** (≈ 10% over-mint) at the expense of existing holders.
7. When the Chainlink feed updates and `updateRSETHPrice()` is called, `rsETHPrice` drops to reflect the true TVL, diluting all prior holders.

**Root cause confirmed:** [1](#0-0) 

**No staleness check, contrasted with the pool oracle that does check:** [2](#0-1) 

**Mint ratio uses the stale price directly:** [3](#0-2) 

**Entry point (unprivileged depositor):** [4](#0-3)

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

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
