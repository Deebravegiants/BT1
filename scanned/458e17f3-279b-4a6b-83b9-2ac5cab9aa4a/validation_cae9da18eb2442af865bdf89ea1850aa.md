### Title
Missing Chainlink Oracle Output Validation Enables Stale/Invalid Price Consumption - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but discards all validation fields, accepting any price — including stale, zero, or negative values — without any sanity checks. This is the oracle used to price LST assets during rsETH minting in `LRTDepositPool`. The same codebase already demonstrates the correct pattern in `ChainlinkOracleForRSETHPoolCollateral`, making the omission in `ChainlinkPriceOracle` a clear inconsistency with a concrete security impact.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price as follows:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All five return values of `latestRoundData()` — `roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound` — are available, but only `answer` (the raw price) is used. The following critical checks are absent:

1. **No stale round check**: `answeredInRound < roundId` is never verified, so a price from a completed-but-not-updated round is silently accepted.
2. **No timestamp freshness check**: `updatedAt` is never compared to `block.timestamp`, so an arbitrarily old price is accepted.
3. **No positive price check**: `price` is cast directly to `uint256` without verifying `price > 0`. A negative `int256` wraps to a massive `uint256`, causing catastrophic over-minting.

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` — used for pool collateral pricing in the same repository — correctly validates all three conditions:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

The vulnerable `ChainlinkPriceOracle` is registered as the price oracle for supported LST assets (e.g., stETH, cbETH) via `LRTOracle.assetPriceOracle`. Its output flows directly into rsETH minting:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

`lrtOracle.getAssetPrice(asset)` delegates to `IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset)`: [4](#0-3) 

---

### Impact Explanation

**Critical — Protocol insolvency / direct theft of user funds.**

- **Stale inflated price scenario**: If a Chainlink feed goes stale at a high price (e.g., during network congestion or sequencer downtime on L2), any depositor calling `depositAsset()` receives more rsETH than the fair share of the underlying TVL. This dilutes all existing rsETH holders, constituting direct theft of their proportional claim on protocol assets.
- **Negative price scenario**: If Chainlink returns a negative `int256` answer (possible during extreme market events or feed misconfiguration), the unchecked `uint256(price)` cast produces a value near `2^256`, causing the minting formula to produce an astronomically large `rsethAmountToMint`. A single deposit would mint enough rsETH to drain the entire protocol, causing insolvency.

---

### Likelihood Explanation

Chainlink feeds going stale is a documented, recurring real-world event — it has occurred during Ethereum network congestion, L2 sequencer outages, and feed deprecations. The `answeredInRound < roundId` staleness condition is a standard Chainlink-documented check that the protocol itself applies in `ChainlinkOracleForRSETHPoolCollateral` but omits here. Any unprivileged depositor can trigger this path by simply calling `depositAsset()` or `depositETH()` on `LRTDepositPool` when the feed is stale.

---

### Recommendation

Apply the same validation pattern already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    // Optionally: if (block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

---

### Proof of Concept

1. Assume stETH/ETH Chainlink feed goes stale at price `2e18` (2 ETH per stETH) while the true price is `1e18`.
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 1e18, 0, "")` depositing 1 stETH.
3. `getRsETHAmountToMint` computes: `(1e18 * 2e18) / rsETHPrice`. With `rsETHPrice ≈ 1e18`, result is `2e18` rsETH.
4. Attacker receives 2 rsETH for 1 stETH worth of collateral — double the fair amount.
5. Attacker redeems 2 rsETH via the withdrawal system, extracting 2× the deposited value from the protocol's TVL, at the expense of existing rsETH holders.

For the negative price path: if `price = -1`, then `uint256(-1) = 2^256 - 1`, and `rsethAmountToMint` overflows or produces a value that mints the entire rsETH supply to the attacker in a single transaction. [5](#0-4) [6](#0-5) [7](#0-6)

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
