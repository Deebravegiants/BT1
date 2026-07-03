The code confirms this is a real vulnerability. Here is the full analysis:

---

### Title
Residual LST Funds Permanently Frozen in `LRTWithdrawalManager` After Asset Removal — (`contracts/LRTWithdrawalManager.sol`)

### Summary
`sweepRemainingAssets` is the sole recovery path for residual LST balances held by `LRTWithdrawalManager`. It is gated by `onlySupportedAsset(asset)`, which reverts if the asset has been removed from `LRTConfig`. The `removeSupportedAsset` guard only checks `getTotalAssetDeposits`, which does **not** include the `LRTWithdrawalManager` balance. An admin can therefore remove an asset while residual funds remain in `LRTWithdrawalManager`, permanently freezing them with no recovery path.

### Finding Description

`sweepRemainingAssets` carries the `onlySupportedAsset(asset)` modifier: [1](#0-0) 

That modifier delegates to `lrtConfig.isSupportedAsset(asset)`: [2](#0-1) 

`LRTConfig.removeSupportedAsset` is the only function that clears `isSupportedAsset`. Its sole safety guard is: [3](#0-2) 

`getTotalAssetDeposits` sums balances across the deposit pool, NDCs, EigenLayer strategies, the converter, and the unstaking vault: [4](#0-3) 

**`LRTWithdrawalManager`'s own ERC-20 balance is absent from this sum.** Once `unlockQueue` calls `unstakingVault.redeem(asset, assetAmountUnlocked)`, the assets move from the unstaking vault (tracked) into `LRTWithdrawalManager` (untracked). After all user withdrawals complete, any residual (e.g., stETH rebase accrual between unlock and claim, or rounding dust) sits in `LRTWithdrawalManager` while `getTotalAssetDeposits` returns zero, satisfying the removal guard.

After `removeSupportedAsset` executes: [5](#0-4) 

every function in `LRTWithdrawalManager` that could move the residual out is also gated by `onlySupportedAsset`:
- `sweepRemainingAssets` — line 398
- `initiateWithdrawal` — line 159
- `instantWithdrawal` — line 220
- `unlockQueue` — line 278

`completeWithdrawal` has no asset-support check but requires an existing unlocked withdrawal request; once all requests are completed there are none left. There is no emergency ERC-20 rescue function.

### Impact Explanation
Any LST balance remaining in `LRTWithdrawalManager` at the time of asset removal becomes permanently unrecoverable. For rebasing tokens such as stETH, residual accrual is a normal, expected outcome of the withdrawal lifecycle, making this a realistic loss of real funds. Impact: **Critical — Permanent freezing of funds**.

### Likelihood Explanation
The trigger requires a privileged `DEFAULT_ADMIN_ROLE` call to `removeSupportedAsset`, which is an intended operational action when deprecating an asset. The admin's only safety check (`getTotalAssetDeposits`) gives a false "all clear" because it does not inspect `LRTWithdrawalManager`. No malicious intent is required; the admin acts in good faith and inadvertently freezes the residual. Likelihood: **Low-Medium** (requires asset deprecation, but the missing accounting makes it easy to trigger accidentally).

### Recommendation
Before clearing `isSupportedAsset`, `removeSupportedAsset` should also verify that `LRTWithdrawalManager` holds no residual balance for the asset, e.g.:

```solidity
address withdrawalManager = getContract(LRTConstants.LRT_WITHDRAW_MANAGER);
uint256 wmBalance = IERC20(asset).balanceOf(withdrawalManager);
if (wmBalance > maxNegligibleAmount) revert CannotRemoveAssetWithDeposits(asset);
```

Alternatively, remove the `onlySupportedAsset` guard from `sweepRemainingAssets` and replace it with a tighter access-control check (e.g., `onlyLRTAdmin`) so that residual balances can always be swept regardless of support status.

### Proof of Concept

```solidity
// 1. Complete all user withdrawals for `asset`, leaving a small residual
//    (e.g., stETH rebase accrual) in LRTWithdrawalManager.
//    At this point getTotalAssetDeposits(asset) == 0.

// 2. Admin removes the asset.
lrtConfig.removeSupportedAsset(asset, tokenIndex);
// Succeeds because getTotalAssetDeposits returns 0.

// 3. Attempt to recover residual.
vm.expectRevert(ILRTConfig.AssetNotSupported.selector);
lrtWithdrawalManager.sweepRemainingAssets(asset);
// Reverts — funds are permanently frozen.

// 4. Confirm no alternative drain path:
//    initiateWithdrawal, instantWithdrawal, unlockQueue all carry onlySupportedAsset → revert.
//    completeWithdrawal requires an existing request → none exist.
```

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L395-399)
```text
    function sweepRemainingAssets(address asset)
        external
        nonReentrant
        onlySupportedAsset(asset)
        onlyLRTManager
```

**File:** contracts/utils/LRTConfigRoleChecker.sol (L65-70)
```text
    modifier onlySupportedAsset(address asset) {
        if (!lrtConfig.isSupportedAsset(asset)) {
            revert ILRTConfig.AssetNotSupported();
        }
        _;
    }
```

**File:** contracts/LRTConfig.sol (L80-84)
```text
        address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);

        if (ILRTDepositPool(depositPool).getTotalAssetDeposits(asset) > maxNegligibleAmount) {
            revert CannotRemoveAssetWithDeposits(asset);
        }
```

**File:** contracts/LRTConfig.sol (L86-88)
```text
        delete isSupportedAsset[asset];
        delete assetStrategy[asset];
        depositLimitByAsset[asset] = 0;
```

**File:** contracts/LRTDepositPool.sol (L385-397)
```text
    function getTotalAssetDeposits(address asset) public view override returns (uint256 totalAssetDeposit) {
        (
            uint256 assetLyingInDepositPool,
            uint256 assetLyingInNDCs,
            uint256 assetStakedInEigenLayer,
            uint256 assetUnstakingFromEigenLayer,
            uint256 assetLyingInConverter,
            uint256 assetLyingUnstakingVault
        ) = getAssetDistributionData(asset);
        uint256 effectiveAssetWithEigenLayer = assetStakedInEigenLayer + assetUnstakingFromEigenLayer;
        return (assetLyingInDepositPool + assetLyingInNDCs + effectiveAssetWithEigenLayer + assetLyingInConverter
                + assetLyingUnstakingVault);
    }
```
