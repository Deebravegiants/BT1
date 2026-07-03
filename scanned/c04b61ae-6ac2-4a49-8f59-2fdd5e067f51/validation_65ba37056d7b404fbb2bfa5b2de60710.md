### Title
Burn Before Availability Check in `instantWithdrawal` Violates CEI Pattern - (File: contracts/LRTWithdrawalManager.sol)

### Summary
In `LRTWithdrawalManager.instantWithdrawal`, rsETH tokens are burned from the caller before verifying that sufficient assets are available in the unstaking vault. This is a direct analog to the external report's class of issue — a destructive state-changing external call executes before a critical guard check, violating the Checks-Effects-Interactions pattern.

### Finding Description
The function `instantWithdrawal` performs the following sequence:

```solidity
// line 228
uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
// line 229 — BURN happens here, before the availability check
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
// line 231-233 — check happens AFTER the burn
if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
    revert CantInstantWithdrawMoreThanAvailable();
}
``` [1](#0-0) 

The `burnFrom` call at line 229 is a destructive external interaction that permanently destroys the caller's rsETH tokens. The critical guard — checking whether the vault actually holds enough assets to satisfy the withdrawal — only executes at lines 231–233, after the burn has already occurred. The correct CEI-compliant order is: (1) compute `assetAmountUnlocked`, (2) check vault availability, (3) burn rsETH, (4) redeem from vault.

This is directly analogous to the external report's `NodeRegistry.removeNode` finding, where `emit LogNodeRemoved(nodes[_nodeIndex].url, ...)` and `delete urlIndex[...]` executed before `assert(length > 0)`, and to `NodeRegistry.instantWithdrawal`-class issues where the recommendation was to validate all inputs and preconditions before performing any state-changing interactions.

### Impact Explanation
**Low.** Solidity's revert mechanism rolls back the burn if the availability check subsequently fails, so no rsETH is permanently lost. However, the pattern violation means a destructive external call (burn) executes unnecessarily before a critical safety check. Users calling `instantWithdrawal` when vault assets are insufficient waste gas on the burn operation before the transaction reverts. The contract fails to deliver the promised efficient instant-withdrawal path and exposes a structural weakness: if rsETH ever gains transfer hooks (e.g., via an upgrade), the burn-before-check ordering becomes an exploitable reentrancy surface despite `nonReentrant` on the outer function.

### Likelihood Explanation
**Medium.** `instantWithdrawal` is a public, permissionless entry point available to any rsETH holder when `isInstantWithdrawalEnabled[asset]` is true. [2](#0-1)  Vault liquidity for instant withdrawal is a finite, separately managed resource (`getAssetsAvailableForInstantWithdrawal`). Under normal protocol operation — especially during high withdrawal demand or after large `unlockQueue` calls — the vault can have insufficient instant-withdrawal liquidity, making the mis-ordered burn a realistic trigger.

### Recommendation
Reorder operations in `instantWithdrawal` to follow the Checks-Effects-Interactions pattern:

```solidity
// 1. All checks first
if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset])
    revert InvalidAmountToWithdraw();
if (IERC20(lrtConfig.rsETH()).balanceOf(msg.sender) < rsETHUnstaked)
    revert NotEnoughRsETH();

uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(
    lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT)
);
if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset))
    revert CantInstantWithdrawMoreThanAvailable();

// 2. Effects / interactions only after all checks pass
IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
unstakingVault.redeem(asset, assetAmountUnlocked);
```

The same CEI violation exists in `initiateWithdrawal`, where `safeTransferFrom` executes before the `ExceedAmountToWithdraw` check: [3](#0-2) 

### Proof of Concept
1. `isInstantWithdrawalEnabled[asset]` is `true`; unstaking vault holds 0 assets available for instant withdrawal.
2. User holds sufficient rsETH and calls `instantWithdrawal(asset, rsETHUnstaked, referralId)`.
3. Amount and balance checks pass (lines 224–227).
4. `assetAmountUnlocked = getExpectedAssetAmount(...)` returns a non-zero value.
5. **`burnFrom(msg.sender, rsETHUnstaked)` executes** — rsETH is burned from the user.
6. `unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)` returns 0.
7. `CantInstantWithdrawMoreThanAvailable` reverts — the burn is rolled back by the EVM.
8. User wasted gas on the burn external call; the vault availability check that should have been first was last. [4](#0-3)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L166-175)
```text
        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
```

**File:** contracts/LRTWithdrawalManager.sol (L212-223)
```text
    function instantWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
        onlyInstantWithdrawalAllowed(asset)
    {
```

**File:** contracts/LRTWithdrawalManager.sol (L228-233)
```text
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }
```
