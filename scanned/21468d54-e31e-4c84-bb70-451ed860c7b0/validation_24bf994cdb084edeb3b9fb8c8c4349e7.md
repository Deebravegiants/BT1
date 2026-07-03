### Title
Unset `queuedWithdrawalsBuffer` Allows Instant Withdrawals to Drain Vault Assets Reserved for Queued Withdrawal Claimants — (`contracts/LRTUnstakingVault.sol`)

---

### Summary

`LRTUnstakingVault.getAssetsAvailableForInstantWithdrawal` returns `vaultBalance - queuedWithdrawalsBuffer[asset]`. Because `queuedWithdrawalsBuffer` is a Solidity mapping that defaults to `0`, and is only set by an explicit operator call, the entire vault balance is available for instant withdrawals whenever the buffer has not been configured. Assets that have been unstaked from EigenLayer and are sitting in the vault awaiting `unlockQueue` — including accrued staking yield — can be fully consumed by instant withdrawers, leaving queued withdrawal users unable to claim.

---

### Finding Description

`queuedWithdrawalsBuffer` is declared as:

```solidity
mapping(address asset => uint256 buffer) public queuedWithdrawalsBuffer;
``` [1](#0-0) 

It is only written by `setQueuedWithdrawalsBuffer`, which is callable exclusively by `onlyLRTOperator`:

```solidity
function setQueuedWithdrawalsBuffer(address asset, uint256 buffer)
    external onlyLRTOperator onlySupportedAsset(asset)
{
    queuedWithdrawalsBuffer[asset] = buffer;
``` [2](#0-1) 

`getAssetsAvailableForInstantWithdrawal` uses this value as the sole guard:

```solidity
availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
``` [3](#0-2) 

When `reservedBuffer == 0` (the default), `availableAmount == vaultBalance` — the entire vault is exposed.

`instantWithdrawal` enforces only this single check before calling `unstakingVault.redeem`:

```solidity
if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
    revert CantInstantWithdrawMoreThanAvailable();
}
unstakingVault.redeem(asset, assetAmountUnlocked);
``` [4](#0-3) 

There is no cross-check against `assetsCommitted` (which tracks assets owed to queued withdrawal users) at the vault level. `assetsCommitted` is only used in `getAvailableAssetAmount`, which gates new queued withdrawal initiations, not instant withdrawals:

```solidity
availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
``` [5](#0-4) 

Meanwhile, `unlockQueue` uses the raw vault balance (`unstakingVault.balanceOf(asset)`) — not `getAssetsAvailableForInstantWithdrawal` — so it has no awareness of how much was already consumed by instant withdrawals:

```solidity
totalAvailableAssets: unstakingVault.balanceOf(asset)
``` [6](#0-5) 

If the vault is drained, `unlockQueue` reverts on `AmountMustBeGreaterThanZero` and queued withdrawal users are stuck.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

The vault accumulates staking yield on top of principal as assets are unstaked from EigenLayer. Queued withdrawal users are entitled to their pro-rata share of that yield (locked in at `initiateWithdrawal` time via `expectedAssetAmount`). An instant withdrawer with sufficient rsETH can consume the entire vault balance — principal plus yield — before `unlockQueue` is called, taking yield that belongs to queued claimants. The queued users have already surrendered their rsETH to the `WithdrawalManager`; they cannot reclaim it and cannot receive their assets until the vault is replenished.

---

### Likelihood Explanation

**Medium.**

The preconditions are:
1. `isInstantWithdrawalEnabled[asset] == true` — an operator action, but a normal operational state.
2. `queuedWithdrawalsBuffer[asset] == 0` — the **default** state; requires no attacker action.
3. The vault holds assets from a completed EigenLayer unstaking cycle while queued withdrawals are pending.

Condition 2 is the default for every asset. An operator who enables instant withdrawal without also setting the buffer (a separate, non-atomic call) leaves the system vulnerable. The window between EigenLayer unstaking completion and `unlockQueue` execution is the attack window. No privileged access is required by the attacker.

---

### Recommendation

1. **Enforce the buffer automatically.** When `unlockQueue` is called, compute the amount owed to pending queued withdrawals (`assetsCommitted[asset]`) and treat that as the minimum buffer, independent of the manually set value.
2. **Alternatively**, in `instantWithdrawal`, subtract `assetsCommitted[asset]` (converted to vault-asset terms) from the available amount, so the vault always retains enough for pending queued claims.
3. **At minimum**, require that `setQueuedWithdrawalsBuffer` is called atomically with `setInstantWithdrawalEnabled` (e.g., a combined setter), or add a check in `setInstantWithdrawalEnabled` that reverts if the buffer is still zero.

---

### Proof of Concept

```solidity
// Setup:
// - queuedWithdrawalsBuffer[ETH] = 0 (default, never set)
// - isInstantWithdrawalEnabled[ETH] = true
// - Vault holds 100 ETH (50 ETH owed to queued withdrawal users, 50 ETH for instant)
// - victim has a pending queued withdrawal for 50 ETH (rsETH already in WithdrawalManager)
// - attacker holds rsETH worth 100 ETH at current oracle price

// Step 1: attacker calls instantWithdrawal
// getAssetsAvailableForInstantWithdrawal returns 100 ETH (buffer = 0)
// check passes: 100 ETH <= 100 ETH
withdrawalManager.instantWithdrawal(ETH_TOKEN, attackerRsETH, "");
// vault is now empty

// Step 2: operator calls unlockQueue for victim
// _createUnlockParams: totalAvailableAssets = unstakingVault.balanceOf(ETH) = 0
// reverts: AmountMustBeGreaterThanZero
// victim cannot complete withdrawal — funds frozen until vault is replenished

// Assert:
assertEq(address(unstakingVault).balance, 0);
vm.expectRevert(ILRTWithdrawalManager.AmountMustBeGreaterThanZero.selector);
withdrawalManager.unlockQueue(ETH_TOKEN, type(uint256).max, ...);
```

### Citations

**File:** contracts/LRTUnstakingVault.sol (L43-43)
```text
    mapping(address asset => uint256 buffer) public queuedWithdrawalsBuffer;
```

**File:** contracts/LRTUnstakingVault.sol (L199-208)
```text
    function setQueuedWithdrawalsBuffer(
        address asset,
        uint256 buffer
    )
        external
        onlyLRTOperator
        onlySupportedAsset(asset)
    {
        queuedWithdrawalsBuffer[asset] = buffer;
        emit QueuedWithdrawalsBufferUpdated(asset, buffer);
```

**File:** contracts/LRTUnstakingVault.sol (L235-238)
```text
        uint256 vaultBalance = balanceOf(asset);
        uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
        availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L231-235)
```text
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L601-603)
```text
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L849-849)
```text
            totalAvailableAssets: unstakingVault.balanceOf(asset)
```
