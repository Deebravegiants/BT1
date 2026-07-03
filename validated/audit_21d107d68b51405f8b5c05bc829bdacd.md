Audit Report

## Title
Withdrawers Forfeit All Yield Accrued During Queue Delay Due to Initiation-Time Price Cap — (File: contracts/LRTWithdrawalManager.sol)

## Summary
When a user calls `initiateWithdrawal()`, their rsETH is transferred to `LRTWithdrawalManager` but not burned, leaving it in `totalSupply()`. The oracle continues to price rsETH using the full supply, so as EigenLayer restaking rewards accrue over the 8–16 day delay, the rsETH price rises. At `unlockQueue()` time, `_calculatePayoutAmount()` caps the user's payout at the initiation-time `expectedAssetAmount`, so the user receives no benefit from the appreciation. The full rsETH is burned but only the capped (lower) asset amount is redeemed from `LRTUnstakingVault`; the surplus remains in the vault and is redistributed to all remaining rsETH holders.

## Finding Description

**Step 1 — rsETH locked but not burned at initiation.**

`initiateWithdrawal()` transfers rsETH to the contract and records a fixed `expectedAssetAmount` at the current oracle price:

```solidity
// LRTWithdrawalManager.sol L166-175
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);
assetsCommitted[asset] += expectedAssetAmount;
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

No burn occurs here. The rsETH sits in `LRTWithdrawalManager` and remains part of `IRSETH.totalSupply()`.

**Step 2 — Oracle price rises while rsETH is locked.**

`LRTOracle._updateRsETHPrice()` computes the price as:

```solidity
// LRTOracle.sol L216, L250
uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply(); // includes locked rsETH
uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

As EigenLayer rewards flow in, `totalETHInProtocol` grows while `rsethSupply` is unchanged (locked rsETH not yet burned), so `newRsETHPrice` rises continuously during the delay.

**Step 3 — Payout capped at initiation-time amount.**

`_calculatePayoutAmount()` returns the minimum of the initiation-time amount and the current value:

```solidity
// LRTWithdrawalManager.sol L833-834
uint256 currentReturn = (request.rsETHUnstaked * rsETHPrice) / assetPrice;
return (request.expectedAssetAmount < currentReturn) ? request.expectedAssetAmount : currentReturn;
```

When the price has risen, `currentReturn > expectedAssetAmount`, so the user receives `expectedAssetAmount` — the lower, stale amount.

**Step 4 — Full rsETH burned, only capped amount redeemed.**

```solidity
// LRTWithdrawalManager.sol L305-307
if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
unstakingVault.redeem(asset, assetAmountUnlocked); // only the capped sum
```

The entire `rsETHUnstaked` is burned, but only `assetAmountUnlocked` (the sum of capped payouts) is pulled from `LRTUnstakingVault`. The surplus — the yield that accrued during the delay — remains in the vault. Because `rsethSupply` is now reduced (burn completed) while the vault's asset balance is not fully drawn down, the next oracle price update reflects a higher asset-per-rsETH ratio, redistributing the surplus to all remaining holders.

**Existing guards are insufficient.** The price bounds passed to `unlockQueue()` (`minimumRsEthPrice`, `maximumRsEthPrice`) only prevent processing at manipulated prices; they do not alter the cap logic. The `assetsCommitted` accounting correctly prevents over-withdrawal but does not compensate the withdrawer for yield lost during the delay.

## Impact Explanation

**High — Theft of unclaimed yield.**

Every user who follows the standard `initiateWithdrawal()` → `unlockQueue()` → `completeWithdrawal()` path loses all restaking yield that accrues on their rsETH during the mandatory delay. The yield is not destroyed; it is transferred to remaining rsETH holders. For a 10 ETH withdrawal over an 8-day delay at 5% annual restaking yield, the loss is approximately `10 × 0.05 × 8/365 ≈ 0.011 ETH`. This scales linearly with withdrawal size, delay length, and current APY, and affects every queued withdrawal unconditionally.

## Likelihood Explanation

**High.** The standard withdrawal path is the primary exit mechanism for all rsETH holders. No special conditions, attacker role, or external dependency is required. The rsETH price appreciates continuously as EigenLayer rewards accrue, so every queued withdrawal during any period of positive yield is affected. The only scenario where no yield is lost is if the rsETH price does not change at all during the delay, which is the degenerate case.

## Recommendation

1. **Burn rsETH at initiation time** rather than at unlock time. This removes the locked rsETH from `totalSupply()` immediately, so the price appreciation is not diluted by tokens already committed to exit, and the withdrawer's share of future rewards is correctly zeroed out at the moment they exit.
2. Alternatively, **use the rsETH price at unlock time** as the basis for the payout, removing the initiation-time cap. This ensures the user receives the full current value of their rsETH when the queue is processed.
3. If the cap-at-initiation design is intentional (e.g., to protect against oracle manipulation), document it explicitly as a known trade-off and consider a separate yield-accrual mechanism (e.g., a pro-rata share of rewards earned during the delay period) to compensate withdrawers.

## Proof of Concept

1. rsETH price = 1.05 ETH/rsETH. User calls `initiateWithdrawal(stETH, 100e18)`.
   - 100 rsETH transferred to `LRTWithdrawalManager` (not burned).
   - `expectedAssetAmount` = `100 × 1.05 / 1.0` = 105 stETH recorded.
2. 8 days pass. EigenLayer rewards push rsETH price to 1.06 ETH/rsETH (1 ETH of new rewards on 100 rsETH worth of assets).
3. Operator calls `unlockQueue(stETH, ...)`.
   - `_calculatePayoutAmount`: `currentReturn = 100 × 1.06 / 1.0 = 106`. Returns `min(105, 106) = 105`.
   - 100 rsETH burned; only 105 stETH redeemed from vault.
4. User calls `completeWithdrawal(stETH)` and receives **105 stETH**.
5. The 1 stETH difference remains in `LRTUnstakingVault`. With 100 rsETH now burned and 1 stETH surplus in the vault, the next `updateRSETHPrice()` call reflects a higher price for all remaining holders. The withdrawer provided an 8-day interest-free loan of yield on 100 rsETH with no recourse.

**Foundry fork test plan:** Fork mainnet, deploy/use existing contracts, call `initiateWithdrawal` for a known amount, advance time by 8 days (`vm.warp`), call `updateRSETHPrice` to reflect accrued rewards, call `unlockQueue`, assert that `assetAmountUnlocked < rsETHBurned × newRsETHPrice / assetPrice`, and assert that `LRTUnstakingVault.balanceOf(asset)` retains the surplus.