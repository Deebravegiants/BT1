### Title
Missing Chainlink Price Feed Staleness Validation Allows Stale Prices to Corrupt rsETH Minting and Price Updates - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` discards all Chainlink `latestRoundData()` return values except `price`, performing no staleness or validity checks. A stale or zero price is silently accepted and propagated into rsETH minting calculations and the rsETH price update, directly harming depositors and rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but ignores `roundId`, `updatedAt`, and `answeredInRound`:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L52
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

No check is made for:
- `answeredInRound < roundId` (stale round)
- `updatedAt == 0` (incomplete round)
- `price <= 0` (invalid/zero price)

The same codebase already implements all three checks in `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L30-32
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

`ChainlinkPriceOracle` is the oracle used for all supported LST assets (stETH, ETHx, etc.) in the core protocol. Its `getAssetPrice()` is consumed by:

1. `LRTOracle.getAssetPrice()` → `_getTotalEthInProtocol()` → `_updateRsETHPrice()` — the rsETH/ETH exchange rate
2. `LRTDepositPool.getRsETHAmountToMint()` — the rsETH amount minted per deposit
3. `LRTDepositPool.getSwapETHToAssetReturnAmount()` / `getSwapAssetForETHReturnAmount()` — swap return amounts

---

### Impact Explanation

When a Chainlink feed goes stale (network congestion, sequencer downtime on L2, or a feed that has not been updated within its heartbeat), `ChainlinkPriceOracle` returns the last cached price without any signal of its age.

- **Inflated stale price**: Depositors receive more rsETH than their assets are worth, diluting existing rsETH holders and constituting theft of unclaimed yield.
- **Deflated stale price**: Depositors receive fewer rsETH tokens than owed; the protocol under-mints, causing loss to depositors.
- **rsETH price corruption**: `updateRSETHPrice()` is public and callable by anyone. A stale asset price fed into `_getTotalEthInProtocol()` produces an incorrect `newRsETHPrice`, which is then stored as the canonical `rsETHPrice` used for all subsequent minting and withdrawal calculations.

**Impact: High** — Theft of unclaimed yield / share mis-accounting affecting all depositors and rsETH holders.

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 24 hours for ETH/USD on mainnet, 1 hour on some L2s). During periods of low volatility, feeds may not update for the full heartbeat duration. Any network disruption, sequencer downtime (on L2 deployments), or feed-specific issue can cause staleness. The attacker entry path requires no special permissions — `depositAsset()` and `updateRSETHPrice()` are both publicly callable.

**Likelihood: Medium** — Staleness events are infrequent but realistic, especially on L2 deployments.

---

### Recommendation

Apply the same staleness and validity checks already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Additionally, consider adding a configurable `maxStaleness` threshold (e.g., per-feed heartbeat + buffer) and reverting if `block.timestamp - updatedAt > maxStaleness`.

---

### Proof of Concept

1. A Chainlink LST/ETH feed (e.g., stETH/ETH) goes stale — its last reported price is 1.05 ETH per stETH, but the actual market price has dropped to 0.95 ETH per stETH.
2. Attacker (or any user) calls `LRTDepositPool.depositAsset(stETH, 1000e18)`.
3. `getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale `1.05e18`.
4. rsETH minted = `(1000e18 * 1.05e18) / rsETHPrice` — ~10.5% more rsETH than the depositor's assets are actually worth.
5. Existing rsETH holders are diluted by the excess minted supply.
6. Separately, anyone calls `LRTOracle.updateRSETHPrice()` with the stale price, corrupting the stored `rsETHPrice` used for all future operations.

**Root cause line**: [1](#0-0) 

**Contrast — correct validation in the same repo**: [2](#0-1) 

**Propagation into rsETH minting**: [3](#0-2) 

**Propagation into rsETH price update**: [4](#0-3) 

**Public entry point — no access control**: [5](#0-4)

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

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
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
