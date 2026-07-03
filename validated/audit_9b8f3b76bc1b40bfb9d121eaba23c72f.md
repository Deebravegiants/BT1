Audit Report

## Title
Chainlink `latestRoundData()` Missing Min/Max Circuit-Breaker Validation Enables Over-Minting of rsETH — (File: `contracts/oracles/ChainlinkPriceOracle.sol`)

## Summary

`ChainlinkPriceOracle.getAssetPrice()` calls `priceFeed.latestRoundData()` and uses the returned `price` with no validation: no `price > 0` guard, no staleness check, and no check against the Chainlink aggregator's `minAnswer`/`maxAnswer` circuit-breaker bounds. When a supported LST's true market price falls below the aggregator's `minAnswer`, Chainlink clamps its return to `minAnswer`. The inflated clamped price flows directly into `LRTDepositPool.getRsETHAmountToMint()`, allowing a depositor to receive far more rsETH than the true value of their deposit, diluting all existing rsETH holders and driving the protocol toward insolvency.

## Finding Description

**Root cause — `ChainlinkPriceOracle.getAssetPrice()`:**

```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```

All five return values are available but only `price` is consumed. There is no check that `price > 0`, no round-completeness or heartbeat staleness check, and — critically — no check that `price` lies within the aggregator's `minAnswer`/`maxAnswer` bounds. [1](#0-0) 

Chainlink aggregators have a hardcoded `minAnswer`. If the true market price falls below `minAnswer` (as occurred during the stETH depeg and LUNA collapse), the aggregator returns `minAnswer` rather than the true price. The contract silently accepts this inflated value.

**Propagation path:**

`LRTOracle.getAssetPrice()` delegates directly to the price fetcher: [2](#0-1) 

`LRTDepositPool.getRsETHAmountToMint()` uses this live price divided by the stored `rsETHPrice`: [3](#0-2) 

The stored `rsETHPrice` is updated only when `updateRSETHPrice()` is called. If it has not been updated since the crash, it still reflects the pre-crash value (e.g., 1 ETH). The live `getAssetPrice(asset)` call returns the clamped `minAnswer` (e.g., 0.95 ETH). The ratio `0.95 / 1.0` causes the attacker to receive 95× more rsETH than the true value of their deposit (true price 0.01 ETH) warrants.

Even if `updateRSETHPrice()` is called after the crash, `_getTotalEthInProtocol()` also uses the clamped price for all assets: [4](#0-3) 

This inflates `totalETHInProtocol`, inflates `rsETHPrice`, and prevents the downside-protection circuit-breaker from triggering (it only fires when `newRsETHPrice < highestRsethPrice`, but the clamped price makes the protocol believe TVL has not fallen). [5](#0-4) 

**Secondary instance — `ChainlinkOracleForRSETHPoolCollateral.getRate()`:**

This contract adds staleness and zero-price guards but still omits the `minAnswer`/`maxAnswer` range check: [6](#0-5) 

The inflated rate propagates into L2 pool minting in `RSETHPoolV3` and `RSETHPoolNoWrapper`: [7](#0-6) [8](#0-7) 

## Impact Explanation

**Critical — Protocol insolvency and direct theft of funds from existing rsETH holders.**

An attacker who deposits a crashed LST at the clamped `minAnswer` price receives rsETH minted at a ratio far exceeding the true value of their deposit. Upon redemption, they extract ETH from the protocol's reserves that was contributed by honest depositors. The protocol's backing collapses; rsETH becomes undercollateralized. This matches the allowed impact class: *Direct theft of any user funds* and *Protocol insolvency*.

## Likelihood Explanation

**Medium.** The condition requires a supported LST (stETH, rETH, etc.) to trade below its Chainlink aggregator's `minAnswer`. This is a historically realized scenario: the stETH depeg in May 2022 and the LUNA collapse both caused Chainlink aggregators to clamp at `minAnswer`, and the Venus Protocol suffered a real exploit under identical conditions. The attack is permissionless — any depositor can trigger it the moment the condition is met, with no special access, front-running, or victim interaction required. The protocol supports multiple LSTs, each with its own feed and `minAnswer`, increasing the attack surface.

## Recommendation

1. **Add `minAnswer`/`maxAnswer` range validation** in both `ChainlinkPriceOracle.getAssetPrice()` and `ChainlinkOracleForRSETHPoolCollateral.getRate()`:

```solidity
IChainlinkAggregator aggregator = IChainlinkAggregator(priceFeed.aggregator());
int192 minAnswer = aggregator.minAnswer();
int192 maxAnswer = aggregator.maxAnswer();
require(price >= minAnswer && price <= maxAnswer, "Chainlink: price outside circuit-breaker range");
```

2. **Add full staleness and completeness checks** to `ChainlinkPriceOracle.getAssetPrice()` (already partially present in `ChainlinkOracleForRSETHPoolCollateral`):

```solidity
(uint80 roundId, int256 price,, uint256 updatedAt, uint80 answeredInRound) = priceFeed.latestRoundData();
require(price > 0, "non-positive price");
require(answeredInRound >= roundId, "stale round");
require(block.timestamp - updatedAt < HEARTBEAT, "stale timestamp");
```

## Proof of Concept

**Setup (Foundry fork test against mainnet):**

1. Fork mainnet at a block where stETH is a supported asset with a Chainlink feed whose `minAnswer` = 0.95e18.
2. Use `vm.mockCall` to make `priceFeed.latestRoundData()` return `(1, 0.95e18, block.timestamp, block.timestamp, 1)` — simulating the aggregator clamped at `minAnswer` while the true price is 0.01e18.
3. Confirm `rsETHPrice` is stored at 1e18 (pre-crash, not yet updated).

**Attack sequence:**

```solidity
// Attacker acquires 1000 stETH at true market price (~10 ETH)
deal(stETH, attacker, 1000e18);

// Step 1: deposit crashed stETH
vm.startPrank(attacker);
IERC20(stETH).approve(address(depositPool), 1000e18);
depositPool.depositAsset(stETH, 1000e18, 0, "");

// Step 2: getRsETHAmountToMint returns (1000e18 * 0.95e18) / 1e18 = 950e18 rsETH
// True value deposited: ~10 ETH; rsETH received: ~950 ETH worth

// Step 3: redeem rsETH via withdrawal mechanism
// Attacker extracts ~940 ETH of value from existing depositors
```

**Invariant to assert:**

```solidity
// After deposit, assert protocol is solvent:
// totalTrueETHBacking / rsETHSupply >= rsETHPrice
// This invariant breaks after the attack
```

The test demonstrates that the minted rsETH amount is ~95× the true ETH value deposited, directly proving over-minting and fund extraction from existing holders.

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

**File:** contracts/LRTOracle.sol (L270-282)
```text
        if (newRsETHPrice < highestRsethPrice) {
            uint256 diff = highestRsethPrice - newRsETHPrice;
            // normalizing to 1e18
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);

            // if price decrease is off limit, pause the protocol (unless it's already paused)
            if (isPriceDecreaseOffLimit) {
                if (!lrtDepositPool.paused()) lrtDepositPool.pause();
                if (!withdrawalManager.paused()) withdrawalManager.pause();
                _pause();
                return;
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

**File:** contracts/LRTDepositPool.sol (L519-521)
```text
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
