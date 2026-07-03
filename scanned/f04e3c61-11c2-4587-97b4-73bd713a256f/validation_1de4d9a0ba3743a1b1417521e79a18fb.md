### Title
Stale Chainlink Price Data Used Without Validation in rsETH Minting and Price Calculation - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` consumes raw Chainlink `latestRoundData()` output without validating staleness, round completeness, or price sign. This unvalidated external data flows directly into rsETH minting and the protocol-wide price update, enabling over-minting of rsETH against stale inflated LST prices and causing protocol insolvency.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` and silently discards all validation fields:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

The full return signature is `(roundId, answer, startedAt, updatedAt, answeredInRound)`. None of the following checks are performed:
- `updatedAt` against a heartbeat threshold (staleness)
- `answeredInRound >= roundId` (incomplete round)
- `price > 0` (negative or zero answer)

By contrast, the pool-level oracle wrapper in the same repository performs all three checks:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
``` [2](#0-1) 

This inconsistency confirms the protocol is aware of the requirement but omitted it from the core L1 oracle.

The unvalidated price propagates through two critical paths:

**Path 1 — rsETH minting per deposit:**
`LRTDepositPool.getRsETHAmountToMint()` calls `lrtOracle.getAssetPrice(asset)` live at deposit time:

```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [3](#0-2) 

**Path 2 — Protocol-wide rsETH price update:**
`LRTOracle._getTotalEthInProtocol()` aggregates all asset values using the same unvalidated oracle:

```solidity
uint256 assetER = getAssetPrice(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
``` [4](#0-3) 

### Impact Explanation
**Critical — Protocol insolvency.**

When Chainlink returns a stale inflated price for an LST asset (e.g., stETH/ETH feed has not updated after a slashing event, or during network congestion within the 24-hour heartbeat window):

1. `getAssetPrice(stETH)` returns the stale high value (e.g., 1.05 ETH) while the true value is lower (e.g., 1.00 ETH after slashing).
2. A depositor calling `depositAsset(stETH, amount, ...)` receives `amount * 1.05e18 / rsETHPrice` rsETH — more than the actual ETH value of their deposit.
3. This over-minting dilutes all existing rsETH holders: the total rsETH supply grows faster than the underlying ETH backing, making the protocol insolvent.

Additionally, if `price` is ever returned as a negative `int256` (technically possible from a misconfigured or malicious feed), `uint256(price)` wraps to a near-`type(uint256).max` value, causing catastrophic over-minting in a single transaction.

The `pricePercentageLimit` guard in `_updateRsETHPrice()` does not protect deposits: it only fires when the stored `rsETHPrice` is being updated, not during individual deposit minting. Deposits can over-mint rsETH continuously between price update calls. [5](#0-4) 

### Likelihood Explanation
**Medium-High.** Chainlink heartbeat intervals for LST/ETH pairs are typically 24 hours. During any network congestion, oracle downtime, or within the heartbeat window after a significant LST price movement (e.g., slashing), the feed will return stale data. No attacker action is required — any ordinary depositor transacting during a stale-price window triggers the over-minting. The scenario is realistic and has occurred on mainnet for other protocols.

### Recommendation
Add staleness and validity checks to `ChainlinkPriceOracle.getAssetPrice()`, mirroring the pattern already used in `ChainlinkOracleForRSETHPoolCollateral`:

```solidity
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

    (uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
        priceFeed.latestRoundData();

    if (answeredInRound < roundId) revert StalePrice();
    if (updatedAt == 0 || block.timestamp - updatedAt > MAX_STALENESS) revert StalePrice();
    if (price <= 0) revert InvalidPrice();

    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

`MAX_STALENESS` should be set per asset based on the Chainlink feed's documented heartbeat interval.

### Proof of Concept

1. Assume stETH/ETH Chainlink feed has a 24-hour heartbeat. At T=0 the price is 1.05 ETH. At T=1h a slashing event drops the true value to 1.00 ETH, but the feed has not updated.
2. At T=2h, a depositor calls `LRTDepositPool.depositAsset(stETH, 1e18, 0, "")`.
3. `getRsETHAmountToMint(stETH, 1e18)` calls `lrtOracle.getAssetPrice(stETH)` → `ChainlinkPriceOracle.getAssetPrice(stETH)` → returns stale `1.05e18`.
4. `rsethAmountToMint = (1e18 * 1.05e18) / rsETHPrice`. If `rsETHPrice = 1.05e18`, user receives `1e18` rsETH.
5. Actual ETH value deposited is `1.00 ETH`; rsETH minted represents `1.05 ETH` of claim. The 0.05 ETH difference is extracted from existing holders.
6. This repeats for every depositor until `updateRSETHPrice()` is called, at which point the `pricePercentageLimit` guard may pause the protocol — but the over-minted rsETH already exists and cannot be recalled. [6](#0-5) [7](#0-6)

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

**File:** contracts/LRTDepositPool.sol (L515-521)
```text
        // setup oracle contract
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);

        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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

**File:** contracts/LRTOracle.sol (L339-343)
```text
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
