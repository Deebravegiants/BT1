Audit Report

## Title
Stale `rsETHPrice` Read in `initiateWithdrawal` and `instantWithdrawal` Without Prior `updateRSETHPrice()` Call - (File: contracts/LRTWithdrawalManager.sol)

## Summary
`LRTWithdrawalManager.initiateWithdrawal()` and `instantWithdrawal()` both read `lrtOracle.rsETHPrice()` — a stored, manually-updated state variable — without first calling `updateRSETHPrice()`. In the normal upward-price scenario, users who call `initiateWithdrawal` are locked into a stale-lower `expectedAssetAmount` and are systematically underpaid at unlock time. In the downward-price scenario (e.g., EigenLayer slashing), an attacker calling `instantWithdrawal` redeems more assets from the unstaking vault than their rsETH is currently worth, bypassing the downside-protection pause that would otherwise trigger inside `_updateRsETHPrice()`.

## Finding Description

`LRTOracle.rsETHPrice` is a stored state variable written only inside `_updateRsETHPrice()`:

```solidity
// contracts/LRTOracle.sol L313
rsETHPrice = newRsETHPrice;
```

`updateRSETHPrice()` is public and callable by anyone, but nothing in the withdrawal path calls it:

```solidity
// contracts/LRTOracle.sol L87-89
function updateRSETHPrice() public whenNotPaused {
    _updateRsETHPrice();
}
```

`getExpectedAssetAmount()` reads the stored value directly:

```solidity
// contracts/LRTWithdrawalManager.sol L593
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```

Both `initiateWithdrawal` (L168) and `instantWithdrawal` (L228) call `getExpectedAssetAmount` without first refreshing the price.

**Scenario A — stale price lower than actual (rewards accrued, normal operation):**

`initiateWithdrawal` computes `expectedAssetAmount` with the stale-lower price and stores it in `assetsCommitted[asset]`. When `unlockQueue` later runs with a refreshed price, `_calculatePayoutAmount` returns `min(request.expectedAssetAmount, currentReturn)`. Because `expectedAssetAmount` was computed with the stale-lower price, it is less than `currentReturn`, so the user receives the stale-lower amount. The difference is silently retained by the protocol. This is a systematic underpayment of every user who initiates a withdrawal during a price-lag window.

**Scenario B — stale price higher than actual (slashing event, price decreased):**

`instantWithdrawal` computes `assetAmountUnlocked` using the stale-higher stored price, burns the user's rsETH, then calls `unstakingVault.redeem(asset, assetAmountUnlocked)`. The vault transfers more assets than the current rsETH/asset rate justifies. The downside-protection pause inside `_updateRsETHPrice()` — which would halt the protocol if the price drop exceeds `pricePercentageLimit` — is never triggered because `updateRSETHPrice()` is never called before the withdrawal executes. The only guard is `getAssetsAvailableForInstantWithdrawal`, which limits per-transaction drain but does not prevent the rate mismatch itself.

## Impact Explanation

**Scenario A:** Contract fails to deliver promised returns — every user who calls `initiateWithdrawal` during a price-lag window receives fewer assets than their rsETH is worth at the current rate. Matches: *Low — Contract fails to deliver promised returns, but doesn't lose value.*

**Scenario B:** An attacker holding rsETH can call `instantWithdrawal` immediately after a slashing event (before `updateRSETHPrice()` is called) and drain more assets from the unstaking vault than their rsETH is currently worth. The vault holds assets belonging to users waiting for queued withdrawals; draining it at an inflated rate constitutes direct theft of those user funds. Matches: *Critical — Direct theft of any user funds.*

The downside-protection mechanism in `_updateRsETHPrice()` (L270–281) is specifically designed to pause the protocol on significant price drops, but it is entirely bypassed in `instantWithdrawal` because the price is never refreshed before the redemption executes.

## Likelihood Explanation

`rsETHPrice` is updated by operators on a periodic schedule (not atomically before every withdrawal). Any user can call `updateRSETHPrice()` themselves, but nothing in `initiateWithdrawal` or `instantWithdrawal` enforces this. For Scenario A, the window between operator updates (hours) is sufficient for rewards to accrue and for the stored price to diverge meaningfully — this is a routine condition, not an edge case. For Scenario B, a slashing event in EigenLayer is rare but well-defined; an attacker monitoring EigenLayer for slashing events can front-run the `updateRSETHPrice()` call and exploit the stale price before the downside-protection pause triggers. Likelihood for Scenario A is **High** (normal operation); for Scenario B is **Medium** (requires a slashing event).

## Recommendation

Call `updateRSETHPrice()` (or an internal equivalent) at the start of both `initiateWithdrawal` and `instantWithdrawal` before reading `lrtOracle.rsETHPrice()`:

```solidity
// At the top of initiateWithdrawal and instantWithdrawal:
ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();
```

This ensures the price used for `expectedAssetAmount` and `assetAmountUnlocked` always reflects the latest protocol state, and guarantees the downside-protection pause fires before any redemption executes in the event of a price drop.

## Proof of Concept

**Scenario B (Critical path):**

1. EigenLayer slashing event occurs; the true rsETH/ETH rate drops from 1.05 to 0.90. `rsETHPrice` stored in `LRTOracle` is still 1.05 (nobody has called `updateRSETHPrice()` yet).
2. Attacker holds 100e18 rsETH. They call `instantWithdrawal(ETH, 100e18, ...)`.
3. `getExpectedAssetAmount` computes `100e18 * 1.05e18 / 1.00e18 = 105 ETH` (stale price).
4. `IRSETH.burnFrom(attacker, 100e18)` — attacker burns rsETH currently worth only 90 ETH at the true rate.
5. `unstakingVault.redeem(ETH, 105 ETH)` — vault transfers 105 ETH to the withdrawal manager.
6. Attacker receives 105 ETH (minus fee) for rsETH worth 90 ETH — a 15 ETH profit at the expense of the vault.
7. The downside-protection pause in `_updateRsETHPrice()` (L270–281) is never triggered because `updateRSETHPrice()` was never called.
8. The `getAssetsAvailableForInstantWithdrawal` check (L231) only limits the per-transaction amount; it does not prevent the rate mismatch.

**Foundry fork test outline:**

```solidity
function test_instantWithdrawal_staleHigherPrice() public {
    // 1. Fork mainnet, set rsETHPrice to 1.05e18 in LRTOracle storage
    // 2. Simulate slashing: reduce EigenLayer strategy shares so true price = 0.90e18
    //    (do NOT call updateRSETHPrice())
    // 3. Fund unstakingVault with 200 ETH
    // 4. Attacker calls instantWithdrawal(ETH, 100e18, "")
    // 5. Assert attacker received ~105 ETH (stale rate) not ~90 ETH (true rate)
    // 6. Assert updateRSETHPrice() would have paused the protocol if called
}
```