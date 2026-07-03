### Title
Stale Chainlink Price Accepted Without Staleness Validation in `ChainlinkPriceOracle.getAssetPrice()` - (File: contracts/oracles/ChainlinkPriceOracle.sol)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but silently discards all return values except `price`. Neither `updatedAt` nor `answeredInRound` is checked, so a stale or incomplete Chainlink round is accepted as valid. This stale price propagates directly into rsETH minting in `LRTDepositPool` and into the rsETH/ETH rate computation in `LRTOracle`, allowing a depositor to receive excess rsETH when a feed is stale at an inflated value, diluting existing rsETH holders.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` reads from Chainlink as follows:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L52
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

All five return values of `latestRoundData()` — `roundId`, `answer`, `startedAt`, `updatedAt`, `answeredInRound` — are available, but only `answer` (`price`) is used. The contract performs no check on:

- `answeredInRound >= roundId` (detects a round whose answer was computed in a prior, stale round)
- `updatedAt != 0` (detects an incomplete round)
- `updatedAt` against `block.timestamp` (detects a heartbeat-expired feed)
- `price > 0` (detects a zero/negative answer)

By contrast, the protocol's own `ChainlinkOracleForRSETHPoolCollateral.getRate()` — used in the L2 pool oracle path — performs all three of these checks and reverts with `StalePrice()`, `IncompleteRound()`, or `InvalidPrice()` accordingly:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L27-32
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The unprotected `ChainlinkPriceOracle` is the oracle registered for supported LST assets (stETH, rETH, etc.) on L1. Its output is consumed in two critical paths:

**Path 1 — rsETH minting per deposit:**
`LRTDepositPool.depositAsset()` → `_beforeDeposit()` → `getRsETHAmountToMint()`:

```solidity
// contracts/LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**Path 2 — rsETH/ETH price update:**
`LRTOracle.updateRSETHPrice()` → `_updateRsETHPrice()` → `_getTotalEthInProtocol()`:

```solidity
// contracts/LRTOracle.sol L339
uint256 assetER = getAssetPrice(asset);
...
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```

In both paths, a stale inflated price for any supported LST asset is accepted without reversion.

---

### Impact Explanation

When a Chainlink feed for a supported LST (e.g., stETH/ETH) is stale at a price higher than the current market price:

- **Path 1:** A depositor calling `depositAsset(stETH, amount, ...)` receives `rsethAmountToMint = amount * stalePriceHigh / rsETHPrice`. Because `stalePriceHigh > actualPrice`, the depositor receives more rsETH than their deposit is worth in ETH. This excess rsETH represents a claim on protocol ETH that was not contributed, diluting the ETH backing of all existing rsETH holders — a theft of their accrued yield.

- **Path 2:** `_updateRsETHPrice()` computes `totalETHInProtocol` using the stale inflated price, producing an inflated `newRsETHPrice`. This inflated price is then stored as `rsETHPrice` and used as the denominator in subsequent minting calculations, compounding the mispricing. It also triggers incorrect protocol fee minting (`protocolFeeInETH` is computed on a phantom TVL increase).

Impact classification: **High — Theft of unclaimed yield** (existing rsETH holders' proportional ETH backing is diluted by excess rsETH minted to the depositor).

---

### Likelihood Explanation

Chainlink feeds have documented heartbeat intervals (e.g., 24 hours for stETH/ETH on mainnet) and deviation thresholds. During periods of network congestion, oracle node downtime, or rapid price movement that has not yet triggered a deviation update, the feed can remain at a stale value for minutes to hours. This is a known, historically observed condition. No privileged access or governance compromise is required — any unprivileged depositor can call `depositAsset()` at any time, including during a period of feed staleness.

---

### Recommendation

Apply the same staleness guards already present in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0) revert IncompleteRound();
    if (price <= 0) revert InvalidPrice();
    // Optionally: if (block.timestamp - updatedAt > HEARTBEAT) revert StalePrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

---

### Proof of Concept

1. Chainlink stETH/ETH feed last updated at `T-2h` with price `1.05e18` (stETH at a premium). Since then, stETH has depegged to `0.98e18` but the feed has not yet triggered a deviation update.

2. Attacker calls `LRTDepositPool.depositAsset(stETH, 100e18, 0, "")`.

3. `getRsETHAmountToMint(stETH, 100e18)` calls `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → `latestRoundData()` returns stale `price = 1.05e18`. No staleness check reverts.

4. `rsethAmountToMint = (100e18 * 1.05e18) / rsETHPrice`. Suppose `rsETHPrice = 1.05e18` (also computed from the same stale feed previously). Then `rsethAmountToMint = 100e18`.

5. At actual price `0.98e18`, the depositor's 100 stETH is worth `98 ETH`, but they receive rsETH representing a claim on `100 ETH` of protocol assets — a `~2 ETH` overmint at the expense of existing rsETH holders.

6. The attacker immediately redeems or holds rsETH, capturing the excess ETH value diluted from existing holders. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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
