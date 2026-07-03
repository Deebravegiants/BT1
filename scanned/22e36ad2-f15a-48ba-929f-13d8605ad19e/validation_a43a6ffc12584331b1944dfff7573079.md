### Title
Chainlink `latestRoundData()` Returns Stale/Clamped Price Without Min/Max Validation, Enabling Protocol Insolvency via Inflated Asset Pricing — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

---

### Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `priceFeed.latestRoundData()` with **zero validation** — no staleness check, no `price > 0` guard, and critically no check against Chainlink's aggregator min/max circuit-breaker values. During a market crash, Chainlink aggregators clamp their return value to a configured `minAnswer` rather than reporting the true price. The inflated clamped price propagates into `LRTDepositPool.getRsETHAmountToMint()`, allowing a depositor to receive far more rsETH than the actual value of their crashed LST, directly diluting all existing rsETH holders.

A secondary instance exists in `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`, which checks `ethPrice <= 0` but still omits the min/max range check.

---

### Finding Description

`ChainlinkPriceOracle.getAssetPrice()` fetches the Chainlink price with no validation:

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
``` [1](#0-0) 

All five return values from `latestRoundData()` are available but only `price` is used. There is no check that `price > 0`, no staleness check (`answeredInRound >= roundId`, `updatedAt` heartbeat), and no check that `price` is within the aggregator's `minAnswer`/`maxAnswer` bounds.

Chainlink aggregators have a hardcoded `minAnswer` (e.g., for stETH/ETH this is a small positive value). If the actual market price falls below `minAnswer` — as occurred during the LUNA collapse and stETH depeg events — the aggregator returns `minAnswer` instead of the true price. The contract silently accepts this clamped, inflated value.

This price is consumed by `LRTOracle.getAssetPrice()`: [2](#0-1) 

Which is called by `_getTotalEthInProtocol()` (used to compute `rsETHPrice`) and by `LRTDepositPool.getRsETHAmountToMint()`: [3](#0-2) 

The mint formula is:
```
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

If `getAssetPrice(asset)` returns the clamped `minAnswer` (e.g., 0.95 ETH) while the true market price is 0.01 ETH, the depositor receives ~95× more rsETH than the actual value of their deposit.

The secondary instance in `ChainlinkOracleForRSETHPoolCollateral.getRate()` checks `ethPrice <= 0` but not the min/max range: [4](#0-3) 

This oracle is used in `RSETHPoolV3.viewSwapRsETHAmountAndFee()` and `RSETHPoolNoWrapper.viewSwapRsETHAmountAndFee()` for supported collateral tokens on L2: [5](#0-4) [6](#0-5) 

---

### Impact Explanation

**Critical — Protocol insolvency / direct theft of funds from existing rsETH holders.**

During a market crash of any supported LST (stETH, rETH, etc.):
1. Chainlink clamps the reported price to `minAnswer` (e.g., 0.95 ETH) while the true price is far lower (e.g., 0.01 ETH).
2. An attacker deposits the crashed LST via `LRTDepositPool.depositAsset()`.
3. `getRsETHAmountToMint()` uses the inflated `minAnswer` price, minting ~95× more rsETH than the deposited value warrants.
4. The attacker redeems rsETH for ETH, extracting value from the protocol's reserves.
5. All existing rsETH holders are diluted; the protocol becomes insolvent.

The same attack applies on L2 via `RSETHPoolV3.deposit(token, amount, referralId)` and `RSETHPoolNoWrapper.deposit(token, amount, referralId)` when a supported collateral token crashes.

---

### Likelihood Explanation

**Medium.** The condition requires a supported LST to crash below its Chainlink `minAnswer`. This is a known, historically realized scenario (stETH depeg in 2022, LUNA collapse). The protocol supports multiple LSTs (stETH, rETH, etc.), each with its own Chainlink feed and `minAnswer`. The attack is permissionless — any depositor can exploit it the moment the condition is met, with no front-running or special access required.

---

### Recommendation

1. Fetch `minAnswer` and `maxAnswer` from the Chainlink aggregator's `AggregatorV2V3Interface` and revert if the returned price is outside bounds:

```solidity
IChainlinkAggregator aggregator = IChainlinkAggregator(priceFeed.aggregator());
int192 minAnswer = aggregator.minAnswer();
int192 maxAnswer = aggregator.maxAnswer();

require(price >= minAnswer && price <= maxAnswer, "Chainlink: price outside min/max range");
```

2. Add staleness and round-completeness checks:

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();
require(price > 0, "Chainlink: non-positive price");
require(answeredInRound >= roundId, "Chainlink: stale price");
require(block.timestamp - updatedAt < HEARTBEAT, "Chainlink: stale price");
require(price >= minAnswer && price <= maxAnswer, "Chainlink: price outside circuit breaker range");
```

Apply the same fix to `ChainlinkOracleForRSETHPoolCollateral.getRate()`.

---

### Proof of Concept

1. Assume stETH is a supported asset with a Chainlink feed whose `minAnswer` = 0.95e18 (95% of ETH).
2. A market event causes stETH's true price to drop to 0.01e18 (1% of ETH).
3. Chainlink's aggregator clamps the return to `minAnswer` = 0.95e18.
4. Attacker acquires 1000 stETH at market price (~10 ETH worth).
5. Attacker calls `LRTDepositPool.depositAsset(stETH, 1000e18, 0, "")`.
6. `getRsETHAmountToMint` computes: `(1000e18 * 0.95e18) / rsETHPrice` — using the clamped price.
7. Attacker receives rsETH worth ~950 ETH instead of ~10 ETH.
8. Attacker redeems rsETH, extracting ~940 ETH of value from existing protocol depositors.
9. The protocol's backing collapses; rsETH becomes undercollateralized. [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/oracles/ChainlinkPriceOracle.sol (L49-55)
```text
    function getAssetPrice(address asset) external view onlySupportedAsset(asset) returns (uint256) {
        AggregatorV3Interface priceFeed = AggregatorV3Interface(assetPriceFeed[asset]);

        (, int256 price,,,) = priceFeed.latestRoundData();

        return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
    }
```

**File:** contracts/LRTOracle.sol (L156-158)
```text
    function getAssetPrice(address asset) public view onlySupportedOracle(asset) returns (uint256) {
        return IPriceFetcher(assetPriceOracle[asset]).getAssetPrice(asset);
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

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-36)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
```

**File:** contracts/pools/RSETHPoolV3.sol (L331-334)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L307-311)
```text
        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```
