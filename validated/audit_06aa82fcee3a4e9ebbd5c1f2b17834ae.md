Audit Report

## Title
Stale `rsETHPrice` Used in Deposit and Instant Withdrawal Flows Due to Missing Atomic Price Update - (`contracts/LRTOracle.sol`, `contracts/LRTDepositPool.sol`, `contracts/LRTWithdrawalManager.sol`)

## Summary
`LRTOracle.rsETHPrice` is a cached state variable updated only when `updateRSETHPrice()` is explicitly called. Neither `LRTDepositPool.depositAsset()`/`depositETH()` nor `LRTWithdrawalManager.instantWithdrawal()` invoke `updateRSETHPrice()` before reading `rsETHPrice`. This allows any unprivileged user to exploit the gap between the stale cached price and the real current price to receive excess rsETH on deposit (stealing accrued yield from existing holders) or excess underlying assets on instant withdrawal (direct fund theft).

## Finding Description

**Root cause:** `rsETHPrice` is a storage variable written only inside `_updateRsETHPrice()`, which is only triggered by an explicit external call to `updateRSETHPrice()` or `updateRSETHPriceAsManager()`. No deposit or instant-withdrawal code path calls either function.

**Deposit path:**
`LRTDepositPool.getRsETHAmountToMint()` computes the rsETH to mint as:
```
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```
This is called from `_beforeDeposit()`, which is invoked by both `depositAsset()` and `depositETH()`. If `rsETHPrice` is stale-low (real price has risen due to staking rewards), the denominator is smaller than it should be, and the depositor receives more rsETH than their deposit warrants.

**Instant withdrawal path:**
`LRTWithdrawalManager.getExpectedAssetAmount()` computes:
```
underlyingToReceive = amount * lrtOracle.rsETHPrice() / lrtOracle.getAssetPrice(asset);
```
This is called directly inside `instantWithdrawal()`. If `rsETHPrice` is stale-high (real price has fallen due to a slashing event not yet reflected), the numerator is inflated and the withdrawer receives more underlying assets than their rsETH is worth.

**Why existing guards are insufficient:**
- `pricePercentageLimit` in `_updateRsETHPrice()` can cause the price to remain stale for *longer* periods: if accumulated rewards push the new price above the threshold, non-manager callers of `updateRSETHPrice()` receive `PriceAboveDailyThreshold` revert, leaving the price frozen until a manager acts. This widens the exploitable window.
- The auto-pause on large price drops (lines 277–281 of `LRTOracle.sol`) mitigates the *largest* slashing scenarios for instant withdrawal, but does not cover moderate slashing events within the `pricePercentageLimit` band.
- The `minRSETHAmountExpected` slippage parameter in deposits protects the depositor from receiving *less* than expected, but does not prevent them from receiving *more* than deserved at the expense of existing holders.

## Impact Explanation

**Deposit — Theft of unclaimed yield (High):** As staking rewards accrue, the real rsETH/ETH rate rises while `rsETHPrice` remains stale-low. Because `rsethAmountToMint = amount * assetPrice / rsETHPrice`, a stale-low denominator yields excess rsETH. The attacker's excess rsETH represents yield that belongs to existing holders, extracted without their consent. This is repeatable on every block where the price has not been updated.

**Instant withdrawal — Direct theft of user funds (Critical):** After a slashing event that has not yet been reflected in `rsETHPrice`, `getExpectedAssetAmount` returns an inflated asset amount. The attacker burns rsETH and receives more underlying assets from the unstaking vault than their rsETH is actually worth, directly draining funds from the vault at the expense of other participants.

## Likelihood Explanation

`updateRSETHPrice()` is not called by any on-chain keeper or bot within the protocol contracts. It is a permissionless `public` function, meaning any user can choose to call it or not. A rational attacker will simply omit the call when the stale price is favorable. Staking rewards accrue continuously, making the deposit vector reliably exploitable over time. The instant withdrawal vector requires a slashing event followed by a delay before the price is updated, which is a narrower but realistic window given the permissionless nature of the price update function.

## Recommendation

Call `updateRSETHPrice()` atomically at the start of `depositAsset()`, `depositETH()`, and `instantWithdrawal()` before any price-dependent computation:

```solidity
// In LRTDepositPool.depositAsset() and depositETH():
ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();

// In LRTWithdrawalManager.instantWithdrawal():
ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE)).updateRSETHPrice();
```

Alternatively, expose `_updateRsETHPrice()` logic as a `view` function that computes the live price on-the-fly without writing to storage, and use that in all price-sensitive calculations instead of the cached `rsETHPrice` variable.

## Proof of Concept

**Deposit exploit (theft of unclaimed yield):**
1. Staking rewards accrue over time; the real rsETH/ETH rate rises from `1.00 ETH` to `1.05 ETH`, but `updateRSETHPrice()` has not been called, so `rsETHPrice` remains `1.00 ETH`.
2. Attacker calls `LRTDepositPool.depositETH{value: 10 ETH}(minRSETH, "")` without first calling `updateRSETHPrice()`.
3. `getRsETHAmountToMint` computes: `10e18 * 1e18 / 1.00e18 = 10 rsETH`. The correct amount at the real price would be `10e18 * 1e18 / 1.05e18 ≈ 9.524 rsETH`.
4. Attacker receives `~0.476 rsETH` more than deserved, extracted from the yield belonging to existing holders.
5. After `updateRSETHPrice()` is eventually called (by anyone), the price updates to `1.05 ETH`. The attacker's rsETH is now worth `10.5 ETH` — a risk-free profit of `~0.476 ETH`.

**Foundry fork test plan:**
```solidity
function testStaleDepositExploit() public {
    // Fork mainnet, advance time to accrue staking rewards
    // Verify rsETHPrice is stale (lower than live computed price)
    // Attacker deposits 10 ETH without calling updateRSETHPrice()
    // Assert attacker received more rsETH than getRsETHAmountToMint would return after a fresh update
    // Call updateRSETHPrice(), assert attacker's rsETH is worth more than 10 ETH
}
```

**Instant withdrawal exploit (direct fund theft):**
1. A slashing event reduces the real rsETH/ETH rate from `1.05 ETH` to `1.00 ETH`, but `updateRSETHPrice()` has not been called, so `rsETHPrice` remains `1.05 ETH`.
2. Attacker calls `instantWithdrawal(asset, rsETHAmount, "")` without calling `updateRSETHPrice()`.
3. `getExpectedAssetAmount` computes: `rsETHAmount * 1.05e18 / assetPrice` — inflated by the stale price.
4. Attacker burns rsETH and receives excess underlying assets from the unstaking vault, directly stealing funds from other participants.