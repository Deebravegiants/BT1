Audit Report

## Title
Inconsistent Zero-Price Handling in `_updateRsETHPrice` Causes Deposit Freeze When `pricePercentageLimit` Is Zero - (File: contracts/LRTOracle.sol)

## Summary
`LRTOracle._updateRsETHPrice` stores a zero `rsETHPrice` when `pricePercentageLimit == 0` (the Solidity default, never set in `initialize`) and `totalETHInProtocol` computes to zero. The downside-protection branch short-circuits on `pricePercentageLimit > 0`, so a zero price bypasses the auto-pause and is persisted on-chain. Once `rsETHPrice == 0`, all L1 and L2 deposit paths revert with a division-by-zero panic, freezing deposits until admin intervention.

## Finding Description
`updateRSETHPrice()` is `public whenNotPaused` with no access control, callable by any external account.

`pricePercentageLimit` is declared as a plain `uint256` state variable and is never assigned in `initialize`, leaving it at the Solidity default of `0`. It is only set by an explicit admin call to `setPricePercentageLimit`.

Inside `_updateRsETHPrice`, the downside-protection check at lines 273–274 reads:
```solidity
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
```
When `pricePercentageLimit == 0`, the short-circuit `pricePercentageLimit > 0` is `false`, so `isPriceDecreaseOffLimit = false` regardless of how far the price has dropped — including to zero. Execution falls through to line 313:
```solidity
rsETHPrice = newRsETHPrice;   // stores 0
```

`newRsETHPrice` reaches zero when `totalETHInProtocol == 0`. `_getTotalEthInProtocol` accumulates `totalAssetAmt.mulWad(assetER)` for each supported asset. `assetER` comes from `ChainlinkPriceOracle.getAssetPrice`, which performs no zero-price guard:
```solidity
(, int256 price,,,) = priceFeed.latestRoundData();
return uint256(price) * 1e18 / 10 ** uint256(priceFeed.decimals());
```
A Chainlink feed returning `0` (a documented failure mode during circuit-breaker events or feed deprecation) propagates silently, yielding `totalETHInProtocol = 0` and thus `newRsETHPrice = 0`.

With `rsETHPrice = 0` stored:
- **L1 deposits**: `LRTDepositPool.getRsETHAmountToMint` at line 520 executes `(amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice()` — division by zero → revert.
- **L2 deposits**: `RSETHPoolV3.viewSwapRsETHAmountAndFee` at line 307 and `RSETHPoolV3ExternalBridge.viewSwapRsETHAmountAndFee` at line 426 execute `amountAfterFee * 1e18 / rsETHToETHrate` where `rsETHToETHrate = getRate() = rsETHPrice = 0` — division by zero → revert.

The inconsistency is confirmed by `RSETHPoolV3ExternalBridge.viewSwapAssetToPremintedRsETH` at lines 523–524, which explicitly guards against zero:
```solidity
if (rsETHToETHrate == 0) revert UnsupportedOracle();
```
while the primary deposit path `viewSwapRsETHAmountAndFee` does not.

## Impact Explanation
All L1 deposits via `LRTDepositPool.depositETH` / `depositAsset` and all L2 deposits via `RSETHPoolV3.deposit` / `RSETHPoolV3ExternalBridge.deposit` revert until an admin manually calls `updateRSETHPriceAsManager` after the oracle recovers or sets a non-zero `pricePercentageLimit`. This constitutes **temporary freezing of funds** (Medium impact), which is a concrete allowed impact in the scope.

## Likelihood Explanation
- `updateRSETHPrice()` is `public whenNotPaused` — any external account can trigger it.
- `pricePercentageLimit` is `0` by default and requires an explicit admin call to set; any deployment window before that call is vulnerable.
- Chainlink returning `0` is a documented failure mode (circuit-breaker events, feed deprecation, sequencer downtime on L2s). A single supported asset with a non-zero balance returning a zero price is sufficient to reduce `totalETHInProtocol` to zero if it is the only asset, or if all assets simultaneously return zero.
- The combination of default-zero `pricePercentageLimit` and a Chainlink zero-price event is realistic, particularly in the deployment window or after a feed update.

## Recommendation
1. **Add a zero-price guard in `_updateRsETHPrice`** before storing the new price (e.g., `if (newRsETHPrice == 0) revert InvalidPrice();`).
2. **Add a zero-price guard in `ChainlinkPriceOracle.getAssetPrice`**, consistent with other oracle contracts in the codebase that already check `if (price <= 0) revert InvalidPrice()`.
3. **Add a zero-rate guard in `viewSwapRsETHAmountAndFee`** (both ETH and token overloads in `RSETHPoolV3` and `RSETHPoolV3ExternalBridge`) to match the explicit check already present in `viewSwapAssetToPremintedRsETH`.
4. **Initialize `pricePercentageLimit` to a non-zero value** in `initialize` so downside protection is active from deployment.

## Proof of Concept
1. Deploy protocol; `pricePercentageLimit == 0` (no admin call to `setPricePercentageLimit` yet).
2. Users deposit, `rsethSupply > 0`, `rsETHPrice = 1 ether`.
3. Chainlink feed for a supported asset (e.g., stETH) returns `0` during a feed anomaly.
4. Any account calls `LRTOracle.updateRSETHPrice()` (public, no access control).
5. `_getTotalEthInProtocol` returns `0` (zero asset price × any balance = 0).
6. `newRsETHPrice = (0 - 0).divWad(rsethSupply) = 0`.
7. Downside-protection check: `isPriceDecreaseOffLimit = (0 > 0) && ... = false` → no pause, no early return.
8. `_checkAndUpdateDailyFeeMintLimit(0)` passes (both `maxFeeMintAmountPerDay` and `currentPeriodMintedFeeAmount` are 0).
9. `rsETHPrice = 0` is stored at line 313.
10. Any user calling `LRTDepositPool.depositETH` hits `getRsETHAmountToMint` → `/ lrtOracle.rsETHPrice()` → division-by-zero panic → revert.
11. Any L2 user calling `RSETHPoolV3.deposit` hits `viewSwapRsETHAmountAndFee` → `/ rsETHToETHrate` (= 0) → division-by-zero panic → revert.
12. All deposits are frozen until admin calls `updateRSETHPriceAsManager` after oracle recovery.