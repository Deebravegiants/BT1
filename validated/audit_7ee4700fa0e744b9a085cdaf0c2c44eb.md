Audit Report

## Title
Stale Cached `rsETHPrice` Allows Depositors to Mint Excess rsETH at an Outdated Exchange Rate — (File: `contracts/LRTOracle.sol`)

## Summary

`LRTOracle` stores `rsETHPrice` as a plain storage variable that is only written when `updateRSETHPrice()` or `updateRSETHPriceAsManager()` is explicitly called. The deposit minting formula in `LRTDepositPool.getRsETHAmountToMint()` divides by this cached value while using a live asset price in the numerator. When staking rewards have accrued inside EigenLayer strategies (raising the true rsETH/ETH rate) but `updateRSETHPrice()` has not yet been called, the stored `rsETHPrice` is stale-low, causing any depositor to receive more rsETH than their deposit is worth and diluting the yield owed to existing holders.

## Finding Description

`rsETHPrice` is declared as a plain `uint256` storage variable in `LRTOracle`:

```solidity
// LRTOracle.sol L28
uint256 public override rsETHPrice;
```

It is written exclusively inside `_updateRsETHPrice()`, which is reachable only through two explicit entry-points — the public `updateRSETHPrice()` and the manager-gated `updateRSETHPriceAsManager()`:

```solidity
// LRTOracle.sol L87-96
function updateRSETHPrice() public whenNotPaused { _updateRsETHPrice(); }
function updateRSETHPriceAsManager() external onlyLRTManager { _updateRsETHPrice(); }
```

The deposit flow `depositAsset()` → `_beforeDeposit()` → `getRsETHAmountToMint()` never calls either function. The minting formula is:

```solidity
// LRTDepositPool.sol L520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

`lrtOracle.getAssetPrice(asset)` reads a **live** price from the configured `IPriceFetcher` on every call. `lrtOracle.rsETHPrice()` returns the **cached** storage value. When EigenLayer strategy shares appreciate (e.g., via beacon-chain rewards or LST rebases), `_getTotalEthInProtocol()` would return a higher value than at the last price update, but `rsETHPrice` remains at its last-written value. The denominator is therefore too small, and the formula mints more rsETH than the deposited assets are worth.

`_updateRsETHPrice()` computes the correct price only at call time:

```solidity
// LRTOracle.sol L250
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
// LRTOracle.sol L313
rsETHPrice = newRsETHPrice;
```

Because the attacker's excess rsETH inflates `rsethSupply` before this line executes, the next price update lands lower than it would have, permanently diluting every pre-existing holder's share of TVL.

Existing guards do not prevent this:
- `pricePercentageLimit` limits how large a single price *increase* can be; it does not prevent deposits against a stale-low price.
- `minRSETHAmountExpected` is a depositor-side slippage guard; it protects the attacker, not existing holders.
- The `whenNotPaused` modifier on `updateRSETHPrice()` means that if the oracle is paused, the price cannot be refreshed at all, widening the window.

The same stale value is also propagated to L2 pools via `RSETHRateProvider.getLatestRate()` → `ILRTOracle(rsETHPriceOracle).rsETHPrice()`, feeding `RSETHPoolV2.viewSwapRsETHAmountAndFee()` and `RSETHPoolV3ExternalBridge.viewSwapRsETHAmountAndFee()`.

## Impact Explanation

When `rsETHPrice` is stale-low, a depositor receives rsETH whose aggregate value (at the true rate) exceeds the ETH value of their deposit. The surplus rsETH represents yield that had already accrued to existing holders but had not yet been reflected in the on-chain price. After `updateRSETHPrice()` is called, the new price is computed over the now-enlarged supply, so every pre-existing holder's rsETH is worth fractionally less than it should be. This is a concrete, repeatable **theft of unclaimed yield** from existing rsETH holders — matching the High impact category.

## Likelihood Explanation

`updateRSETHPrice()` is not called automatically; it depends on off-chain keepers or manual invocation. EigenLayer strategy shares appreciate continuously. Any gap between reward accrual and the next price update creates an exploitable window. Because `updateRSETHPrice()` is public and `depositAsset()` is permissionless, an attacker requires no privileged access. An attacker can also observe the keeper's pending `updateRSETHPrice()` transaction in the mempool and front-run it with a large deposit, maximising the captured yield in a single block. The attack is repeatable every reward cycle. Likelihood is **Medium**, yielding an overall **High** severity.

## Recommendation

1. **Refresh price atomically on deposit**: compute the current rsETH price inline inside `getRsETHAmountToMint()` using `_getTotalEthInProtocol()` and `rsETH.totalSupply()` (or expose a view-only equivalent), bypassing the cached storage variable entirely.
2. **Alternatively**, call `_updateRsETHPrice()` at the start of `depositAsset()` and `depositETH()` so the minting formula always uses a freshly computed rate.
3. **For L2 pools**, add a maximum-age check on the rate received from `RSETHRateProvider` and reject swaps when the rate is stale beyond an acceptable threshold.

## Proof of Concept

1. At time T₀, `rsETHPrice = 1.05e18` (last stored). EigenLayer rewards have accrued; true price is `1.06e18`.
2. Attacker calls `LRTDepositPool.depositAsset(stETH, 100e18, 0, "")`.
3. `getRsETHAmountToMint` computes: `100e18 × 1e18 / 1.05e18 ≈ 95.238 rsETH`. At the true price the correct amount is `100e18 × 1e18 / 1.06e18 ≈ 94.340 rsETH`. Attacker receives ~0.898 rsETH excess.
4. Anyone calls `updateRSETHPrice()`. The new price is computed over the enlarged supply (which now includes the attacker's excess rsETH), landing below `1.06e18`. Every pre-existing holder's rsETH is worth fractionally less than it should be.
5. Attacker repeats every reward cycle with no privileged access — only a public `depositAsset()` call.

**Foundry fork test outline**:
```solidity
// 1. Fork mainnet at a block where rewards have accrued since last updateRSETHPrice()
// 2. Record rsETHPrice = lrtOracle.rsETHPrice()
// 3. Compute expectedMint = deposit * getAssetPrice(stETH) / truePrice (via _getTotalEthInProtocol / totalSupply)
// 4. Call depositAsset(stETH, deposit, 0, "")
// 5. Assert rsETH minted > expectedMint (attacker surplus)
// 6. Call updateRSETHPrice()
// 7. Assert new rsETHPrice < truePrice computed in step 3 (dilution confirmed)
```