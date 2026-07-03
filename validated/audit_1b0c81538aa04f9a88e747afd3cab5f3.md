Audit Report

## Title
Stale `rsETHPrice` Mixed With Live Asset Price in `getExpectedAssetAmount` Enables Theft of Depositor Funds — (`contracts/LRTWithdrawalManager.sol`)

## Summary
`LRTWithdrawalManager::getExpectedAssetAmount` computes withdrawal amounts by dividing the stored `lrtOracle.rsETHPrice()` by the live `lrtOracle.getAssetPrice(asset)`. Because `rsETHPrice` is a state variable updated only on explicit calls to `updateRSETHPrice()` or `updateRSETHPriceAsManager()`, a window exists after any LST Chainlink price drop during which the ratio is inflated. An attacker can call `instantWithdrawal` within this window to receive more underlying assets than their rsETH is worth, extracting value from other depositors' backing.

## Finding Description

**Root cause — mismatched price timestamps in `getExpectedAssetAmount`:**

`LRTWithdrawalManager.sol` line 593:
```solidity
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
`lrtOracle.rsETHPrice()` is a stored state variable (`LRTOracle.sol` line 28) set only when `_updateRsETHPrice()` runs. `lrtOracle.getAssetPrice(asset)` (`LRTOracle.sol` lines 156–158) always reads the live Chainlink feed. These two values are evaluated at different points in time.

**Exploit path via `instantWithdrawal`:**

`instantWithdrawal` (`LRTWithdrawalManager.sol` lines 212–253) is a public function (gated only by `whenNotPaused`, `onlySupportedAsset`, `onlySupportedStrategy`, and `onlyInstantWithdrawalAllowed`). It calls `getExpectedAssetAmount` at line 228, burns rsETH at line 229, and redeems the inflated asset amount from the unstaking vault at line 235 — all in one atomic transaction with no subsequent price-check guard.

**Why the pause mechanism does not protect this path:**

`LRTOracle::_updateRsETHPrice()` (lines 270–281) auto-pauses the protocol when the computed new rsETH price drops beyond `pricePercentageLimit`. However, this pause is only triggered when `_updateRsETHPrice()` is actually called. The `instantWithdrawal` path never calls `_updateRsETHPrice()`; it only reads the already-stored `rsETHPrice`. The protocol remains unpaused and `instantWithdrawal` remains callable throughout the entire window between the Chainlink price drop and the next `updateRSETHPrice()` invocation.

**`initiateWithdrawal` path:**

`initiateWithdrawal` (line 168) also stores the inflated `expectedAssetAmount`. The `_calculatePayoutAmount` minimum check (lines 833–834) uses `rsETHPrice` fetched from `lrtOracle.rsETHPrice()` again (line 847 in `_createUnlockParams`), so if rsETHPrice is still stale at `unlockQueue` time, both the stored and recalculated values are inflated and the minimum provides no protection.

## Impact Explanation

**Critical — Direct theft of user funds at-rest.**

The attacker surrenders rsETH worth less ETH than the assets they receive. The surplus is drawn directly from the pool of assets backing other depositors' rsETH. This is not unclaimed yield; it is principal belonging to other users. The PoC below demonstrates a concrete, quantified extraction of ~1.11 stETH (~1 ETH) per 10 rsETH burned, scalable to the full instant-withdrawal liquidity available.

## Likelihood Explanation

Medium-to-High. `updateRSETHPrice()` is a public function callable by anyone, but it is not called atomically with every Chainlink update. Any block gap between a Chainlink price update and the next `updateRSETHPrice()` call is an exploitable window. An attacker monitoring Chainlink feeds can detect the divergence and submit `instantWithdrawal` in the same block as (or immediately after) the Chainlink update, before any keeper or user calls `updateRSETHPrice()`. The only prerequisite is that `isInstantWithdrawalEnabled[asset]` is true, which is a normal operational state for supported assets.

## Recommendation

Replace the stored `lrtOracle.rsETHPrice()` in `getExpectedAssetAmount` with a live computation using the same inputs as `_updateRsETHPrice`: `totalETHInProtocol / rsETHSupply`, where `totalETHInProtocol` is derived from live Chainlink prices at call time. This ensures numerator and denominator are evaluated at the same instant. Alternatively, require that `updateRSETHPrice()` be called atomically within the same transaction before any withdrawal amount is computed, or add a staleness check that reverts if `rsETHPrice` was last updated more than N blocks ago.

## Proof of Concept

1. Protocol state: 100 stETH deposited, 100 rsETH in supply. `rsETHPrice = 1.0e18`. Chainlink stETH/ETH feed = `1.0e18`. `isInstantWithdrawalEnabled[stETH] = true`.
2. Chainlink stETH/ETH feed updates to `0.9e18` (depeg). `rsETHPrice` is **not** updated — no one has called `updateRSETHPrice()` yet.
3. Attacker holds 10 rsETH (fair value at current prices: ~9 ETH).
4. Attacker calls `instantWithdrawal(stETH, 10e18, "")`.
5. `getExpectedAssetAmount(stETH, 10e18)` computes: `10e18 × 1.0e18 / 0.9e18 = 11.111...e18`.
6. 10 rsETH is burned from attacker; `unstakingVault.redeem(stETH, 11.111e18)` executes.
7. Attacker receives ~11.11 stETH (worth ~10 ETH at depegged rate) for rsETH worth only ~9 ETH.
8. ~1.11 stETH (~1 ETH) is extracted from remaining depositors' backing.

**Foundry fork test plan:** Fork mainnet, set `rsETHPrice` to `1e18` via storage slot, manipulate the stETH Chainlink feed answer to `0.9e18`, call `instantWithdrawal` as an unprivileged address, and assert that `assetAmountUnlocked > rsETHUnstaked` (i.e., attacker receives more asset value than rsETH value surrendered).