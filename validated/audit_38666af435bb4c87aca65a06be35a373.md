### Title
Missing Chainlink Response Validation Allows Stale or Invalid Prices to Inflate rsETH Minting - (File: contracts/oracles/ChainlinkPriceOracle.sol)

### Summary
`ChainlinkPriceOracle.getAssetPrice()` calls `latestRoundData()` but performs no validation on the returned `price`, `updatedAt`, or round-completeness fields. The same codebase's `ChainlinkOracleForRSETHPoolCollateral` implements all three required checks. A stale or negative Chainlink price flows directly into `LRTDepositPool.getRsETHAmountToMint()`, allowing a depositor to receive excess rsETH at the expense of existing holders.

### Finding Description
`ChainlinkPriceOracle.getAssetPrice()` fetches the LST/ETH exchange rate from a Chainlink aggregator:

```solidity
// contracts/oracles/ChainlinkPriceOracle.sol L49-55
function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
    AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);
    (, int256 price,,,) = priceFeed.latestRoundData();
    return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
}
```

Three fields returned by `latestRoundData()` are silently discarded: `roundId`, `updatedAt`, and `answeredInRound`. No check is made that:
- `price > 0` — a negative `int256` cast to `uint256` produces a value near `type(uint256).max`
- `timestamp != 0` — a zero timestamp signals an incomplete round
- `answeredInRound >= roundId` — a stale round means the price has not been refreshed

By contrast, `ChainlinkOracleForRSETHPoolCollateral.getRate()` in the same repository performs all three checks:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L27-33
(uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
    AggregatorV3Interface(oracle).latestRoundData();
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

The unvalidated price from `ChainlinkPriceOracle` propagates into two critical paths:

**Path 1 — Deposit minting** (`LRTDepositPool.getRsETHAmountToMint`, line 520):
```solidity
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
`rsETHPrice` is a stored value updated separately. If `getAssetPrice(asset)` returns an inflated value while `rsETHPrice` still reflects the correct rate, the numerator is inflated and the depositor receives excess rsETH.

**Path 2 — rsETH price update** (`LRTOracle._getTotalEthInProtocol`, line 339):
```solidity
uint256 assetER = getAssetPrice(asset);
totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
An inflated `assetER` inflates `totalETHInProtocol`, which inflates `newRsETHPrice`. The `pricePercentageLimit` guard only triggers if `pricePercentageLimit > 0` (it is `0` by default, disabling the guard entirely).

### Impact Explanation
**High — Theft of unclaimed yield / existing holder funds.**

If a Chainlink feed returns a stale high price or a negative price (cast to a near-`type(uint256).max` value), a depositor calling `depositAsset` receives rsETH computed against the inflated asset price but the correct (lower) stored `rsETHPrice`. The excess rsETH represents a claim on ETH that was not deposited, diluting all existing rsETH holders. At the extreme (negative price cast), the minted rsETH amount overflows or is astronomically large, causing protocol insolvency.

### Likelihood Explanation
**Low-Medium.** Chainlink feeds can return stale data during:
- Sequencer downtime on L2 deployments
- Heartbeat misses during network congestion
- Feed deprecation (where `latestRoundData` continues returning the last answer indefinitely)
- Circuit-breaker events where `minAnswer`/`maxAnswer` clamps the reported price away from the true market price

These are documented, real-world failure modes. The attack requires no privileged access — any depositor can call `depositAsset` at the moment a bad price is active.

### Recommendation
Apply the same validation pattern already used in `ChainlinkOracleForRSETHPoolCollateral` to `ChainlinkPriceOracle.getAssetPrice()`:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) =
    priceFeed.latestRoundData();
if (answeredInRound < roundId) revert StalePrice();
if (updatedAt == 0) revert IncompleteRound();
if (price <= 0) revert InvalidPrice();
```

Additionally, consider adding a configurable `heartbeat` staleness threshold (e.g., `block.timestamp - updatedAt > heartbeat`) and ensuring `pricePercentageLimit` is set to a non-zero value at deployment so the rate-of-change guard in `_updateRsETHPrice` is active.

### Proof of Concept

1. Assume `stETH/ETH` Chainlink feed goes stale at price `1.05e18` (last valid answer) while the true price drops to `1.00e18`.
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 1e18)`.
3. `getRsETHAmountToMint` computes: `(1e18 * 1.05e18) / rsETHPrice`. With `rsETHPrice = 1.01e18` (correct stored value), attacker receives `~1.0396e18` rsETH instead of the correct `~0.9901e18` rsETH — a ~5% excess.
4. Attacker initiates withdrawal via `LRTWithdrawalManager`, redeeming the excess rsETH for ETH that was never deposited, extracting value from existing holders.

For the negative-price scenario: if `price = -1` is returned, `uint256(-1) = type(uint256).max ≈ 1.16e77`, making `rsethAmountToMint` effectively unbounded, minting the attacker an astronomically large rsETH balance and rendering the protocol insolvent.

**Relevant code locations:** [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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
