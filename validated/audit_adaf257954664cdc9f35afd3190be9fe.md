Audit Report

## Title
Lack of Time Consideration in `_updateRsETHPrice` Price Threshold Check Causes DoS of Public Price Update and Stale-Price Dilution of Existing rsETH Holders - (File: contracts/LRTOracle.sol)

## Summary
`LRTOracle._updateRsETHPrice()` enforces a `pricePercentageLimit` guard that compares the cumulative price delta from `highestRsethPrice` with no elapsed-time scaling. If the keeper fails to call `updateRSETHPrice()` long enough for legitimate staking rewards to push the price above the threshold, every non-manager call reverts with `PriceAboveDailyThreshold`, leaving `rsETHPrice` stale. New depositors then receive excess rsETH calculated against the stale (lower) price, diluting existing holders' accumulated yield.

## Finding Description
The threshold check at `LRTOracle.sol` lines 252–266 compares the raw delta `newRsETHPrice - highestRsethPrice` against `pricePercentageLimit.mulWad(highestRsethPrice)` with no timestamp tracking or elapsed-time scaling:

```solidity
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 && priceDifference > pricePercentageLimit.mulWad(highestRsethPrice);
if (isPriceIncreaseOffLimit) {
    if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.MANAGER, msg.sender)) {
        revert PriceAboveDailyThreshold();
    }
}
``` [1](#0-0) 

There is no `lastPriceUpdateTimestamp` stored anywhere in the contract, and no scaling of the allowed delta by elapsed time. [2](#0-1) 

The public entry point is callable by anyone: [3](#0-2) 

The manager escape hatch is restricted to `MANAGER` role, blocking ordinary callers and keeper bots: [4](#0-3) 

When the public function is DoS'd, `rsETHPrice` is never updated (line 313 is never reached). The deposit pool is **not** paused — the downside-protection auto-pause only triggers on price *decrease* beyond the limit (lines 270–281), not on an upward-blocked update. Deposits continue using the stale, lower `rsETHPrice`: [5](#0-4) 

A lower denominator in `(amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()` mints more rsETH per unit of ETH deposited than the depositor is entitled to, diluting all existing holders.

## Impact Explanation
**High — Theft of unclaimed yield.** Existing rsETH holders have accumulated staking yield that should be reflected in a higher `rsETHPrice`. During the DoS window, new depositors receive rsETH at the stale (lower) price, minting excess rsETH that dilutes the existing holders' proportional claim on protocol TVL. Every deposit during the window transfers a fraction of existing holders' accumulated yield to the new depositor. Protocol fee minting is also skipped for the entire window, depriving the treasury of earned yield. [6](#0-5) 

## Likelihood Explanation
**Medium.** With `pricePercentageLimit = 1e16` (1%) and ~4% staking APY, the threshold is breached after roughly 90 days without a successful price update. A lower limit (e.g., 0.1%) reduces this to ~9 days. Keeper bot outages, network congestion, or deliberate inaction are all realistic triggers. Once the DoS begins, it is self-sustaining: every subsequent public call also reverts because `highestRsethPrice` is never updated (line 295 is never reached), so the delta only grows. The DoS persists until a manager intervenes via `updateRSETHPriceAsManager()`. [7](#0-6) 

## Recommendation
Track the timestamp of the last successful price update and scale the allowed delta by elapsed time:

```solidity
uint256 elapsed = block.timestamp - lastPriceUpdateTimestamp;
uint256 scaledLimit = pricePercentageLimit * elapsed / 1 days;
bool isPriceIncreaseOffLimit =
    pricePercentageLimit > 0 &&
    priceDifference > scaledLimit.mulWad(highestRsethPrice);
```

Store `lastPriceUpdateTimestamp` and update it at line 313 alongside `rsETHPrice`. Emit it in `RsETHPriceUpdate` so off-chain monitors can detect staleness. Alternatively, if elapsed time is large enough that the observed increase is within the expected per-day rate, skip the revert entirely.

## Proof of Concept
1. Admin sets `pricePercentageLimit = 1e16` (1%).
2. Keeper bot stops calling `updateRSETHPrice()` for 100 days. Staking rewards accrue; the true rsETH/ETH rate rises ~1.1% above `highestRsethPrice`.
3. Any EOA calls `updateRSETHPrice()`. Inside `_updateRsETHPrice()`, `priceDifference > pricePercentageLimit.mulWad(highestRsethPrice)` is `true` and caller is not `MANAGER` → `revert PriceAboveDailyThreshold()`. `rsETHPrice` and `highestRsethPrice` remain at the 100-day-old stale values.
4. The deposit pool is **not** paused (price increased, not decreased).
5. Attacker calls `depositETH{value: 100 ether}(0, "")`. `getRsETHAmountToMint` computes `(100e18 * 1e18) / rsETHPrice_stale`, minting ~1.1% more rsETH than the depositor is entitled to at the true price.
6. Existing rsETH holders' proportional share of TVL is diluted by the excess minted rsETH. The effect compounds with every deposit during the DoS window.
7. DoS continues until a manager calls `updateRSETHPriceAsManager()`.

Foundry fork test plan: fork mainnet, warp `block.timestamp` forward by 100 days, call `updateRSETHPrice()` from an EOA, assert revert `PriceAboveDailyThreshold`, then call `depositETH` and assert the minted rsETH amount exceeds `(depositAmount * assetPrice) / trueRsETHPrice` by the stale-price margin.

### Citations

**File:** contracts/LRTOracle.sol (L28-35)
```text
    uint256 public override rsETHPrice;
    uint256 public pricePercentageLimit;
    uint256 public highestRsethPrice;

    // Daily fee minting limit variables
    uint256 public currentPeriodMintedFeeAmount;
    uint256 public feePeriodStartTime;
    uint256 public maxFeeMintAmountPerDay;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L94-96)
```text
    function updateRSETHPriceAsManager() external onlyLRTManager {
        _updateRsETHPrice();
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

**File:** contracts/LRTOracle.sol (L293-296)
```text
        // update highest price if new price exceeds it
        if (newRsETHPrice > highestRsethPrice) {
            highestRsethPrice = newRsETHPrice;
        }
```

**File:** contracts/LRTOracle.sol (L299-308)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
            }
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
