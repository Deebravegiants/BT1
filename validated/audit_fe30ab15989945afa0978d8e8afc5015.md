### Title
Replacing `LRT_UNSTAKING_VAULT` in `LRTConfig.setContract` While Pending Withdrawal Requests Exist Permanently Freezes User rsETH - (File: contracts/LRTConfig.sol)

### Summary

`LRTConfig._setContract` allows the admin to replace any contract address in `contractMap`, including `LRT_UNSTAKING_VAULT`, without checking whether the old vault still holds assets backing in-flight withdrawal requests. Unlike `updateAssetStrategy`, which guards against replacement when NDC funds are present, `_setContract` has no analogous guard. If the unstaking vault is replaced while users have pending (locked) withdrawal requests, `unlockQueue` will call `redeem` on the new (empty) vault, revert, and leave all queued rsETH permanently frozen inside `LRTWithdrawalManager` with no user-accessible cancel path.

### Finding Description

`LRTConfig._setContract` is the single setter for all protocol contract addresses:

```solidity
function _setContract(bytes32 key, address val) private {
    UtilLib.checkNonZeroAddress(val);
    if (contractMap[key] == val) {
        revert ValueAlreadyInUse();
    }
    contractMap[key] = val;          // replaces existing non-zero address unconditionally
    emit SetContract(key, val);
}
``` [1](#0-0) 

The only guard is a same-value check. There is no check that the old `LRT_UNSTAKING_VAULT` has a zero balance or that `LRTWithdrawalManager` has no pending locked requests.

Contrast this with `updateAssetStrategy`, which explicitly iterates every NDC and reverts if the old strategy still holds funds:

```solidity
if (assetStrategy[asset] != address(0)) {
    for (uint256 i = 0; i < length;) {
        uint256 ndcBalance = IStrategy(assetStrategy[asset]).userUnderlyingView(ndcs[i]);
        if (ndcBalance > 0) {
            revert CannotUpdateStrategyAsItHasFundsNDCFunds(ndcs[i], ndcBalance);
        }
        ...
    }
}
``` [2](#0-1) 

No equivalent protection exists for `LRT_UNSTAKING_VAULT`.

`LRTWithdrawalManager.unlockQueue` resolves the vault address dynamically at call time:

```solidity
ILRTUnstakingVault unstakingVault =
    ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
UnlockParams memory params = _createUnlockParams(lrtOracle, unstakingVault, asset);
if (params.totalAvailableAssets == 0) revert AmountMustBeGreaterThanZero();
...
unstakingVault.redeem(asset, assetAmountUnlocked);
``` [3](#0-2) 

`_createUnlockParams` reads `unstakingVault.balanceOf(asset)` from the new vault:

```solidity
return UnlockParams({
    rsETHPrice: lrtOracle.rsETHPrice(),
    assetPrice: lrtOracle.getAssetPrice(asset),
    totalAvailableAssets: unstakingVault.balanceOf(asset)
});
``` [4](#0-3) 

If the new vault has zero balance, `unlockQueue` reverts unconditionally.

When a user calls `initiateWithdrawal`, their rsETH is transferred into `LRTWithdrawalManager` and `assetsCommitted` is incremented:

```solidity
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
...
assetsCommitted[asset] += expectedAssetAmount;
_addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);
``` [5](#0-4) 

There is no `cancelWithdrawal` function in `LRTWithdrawalManager`. The only path to recover rsETH is through `completeWithdrawal`, which requires the request to first be unlocked by `unlockQueue`. If `unlockQueue` is permanently broken (new vault is empty), the rsETH is frozen.

### Impact Explanation

**Temporary (potentially extended) freeze of user funds — Medium.**

All rsETH deposited into `LRTWithdrawalManager` via `initiateWithdrawal` that has not yet been unlocked is frozen. Users cannot cancel requests, cannot complete withdrawals, and cannot recover their rsETH until the admin either reverts the vault change or migrates assets to the new vault. The freeze duration is entirely at the admin's discretion and could be indefinite if the migration is not handled promptly.

### Likelihood Explanation

**Low-Medium.** Protocol upgrades that replace the unstaking vault are a realistic operational event. The window of vulnerability is any time users have pending locked withdrawal requests during such an upgrade. Given that the withdrawal delay is set to 8 days by default, there will almost always be pending requests during any vault migration. [6](#0-5) 

### Recommendation

Apply the same pattern used in `updateAssetStrategy`: before allowing `LRT_UNSTAKING_VAULT` to be replaced, verify that the old vault's balance for all supported assets is zero, or that `LRTWithdrawalManager` has no pending locked withdrawal requests (`nextLockedNonce[asset] == nextUnusedNonce[asset]` for all assets). Alternatively, add a dedicated `setUnstakingVault` function that enforces these checks, mirroring the guard in `updateAssetStrategy`. [7](#0-6) 

### Proof of Concept

1. User A calls `initiateWithdrawal(stETH, 10e18, "")`. Their 10 rsETH is transferred to `LRTWithdrawalManager`; `assetsCommitted[stETH] += X`.
2. Admin calls `lrtConfig.setContract(LRT_UNSTAKING_VAULT, newEmptyVault)`. `_setContract` succeeds with no checks.
3. Operator calls `unlockQueue(stETH, ...)`. Inside, `unstakingVault = newEmptyVault`; `newEmptyVault.balanceOf(stETH) == 0`; function reverts with `AmountMustBeGreaterThanZero`.
4. User A calls `completeWithdrawal(stETH, "")`. Reverts with `WithdrawalLocked` because `nextLockedNonce` was never advanced.
5. User A has no `cancelWithdrawal` path. Their 10 rsETH is frozen in `LRTWithdrawalManager` indefinitely. [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/LRTConfig.sol (L151-167)
```text
        if (assetStrategy[asset] != address(0)) {
            // get ndcs
            address depositPool = getContract(LRTConstants.LRT_DEPOSIT_POOL);
            address[] memory ndcs = ILRTDepositPool(depositPool).getNodeDelegatorQueue();

            uint256 length = ndcs.length;
            for (uint256 i = 0; i < length;) {
                uint256 ndcBalance = IStrategy(assetStrategy[asset]).userUnderlyingView(ndcs[i]);
                if (ndcBalance > 0) {
                    revert CannotUpdateStrategyAsItHasFundsNDCFunds(ndcs[i], ndcBalance);
                }

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** contracts/LRTConfig.sol (L237-251)
```text
    function setContract(bytes32 contractKey, address contractAddress) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _setContract(contractKey, contractAddress);
    }

    /// @dev private function to set a contract
    /// @param key Contract key
    /// @param val Contract address
    function _setContract(bytes32 key, address val) private {
        UtilLib.checkNonZeroAddress(val);
        if (contractMap[key] == val) {
            revert ValueAlreadyInUse();
        }
        contractMap[key] = val;
        emit SetContract(key, val);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L94-94)
```text
        withdrawalDelayBlocks = 8 days / 12 seconds;
```

**File:** contracts/LRTWithdrawalManager.sol (L150-178)
```text
    function initiateWithdrawal(
        address asset,
        uint256 rsETHUnstaked,
        string calldata referralId
    )
        external
        override
        nonReentrant
        whenNotPaused
        onlySupportedAsset(asset)
        onlySupportedStrategy(asset)
    {
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }

        IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);

        uint256 expectedAssetAmount = getExpectedAssetAmount(asset, rsETHUnstaked);

        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;

        _addUserWithdrawalRequest(asset, rsETHUnstaked, expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L283-307)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));

        UnlockParams memory params = _createUnlockParams(lrtOracle, unstakingVault, asset);

        _validatePrices(
            params.rsETHPrice,
            params.assetPrice,
            minimumRsEthPrice,
            maximumRsEthPrice,
            minimumAssetPrice,
            maximumAssetPrice
        );

        if (params.totalAvailableAssets == 0) revert AmountMustBeGreaterThanZero();

        // Updates and unlocks withdrawal requests up to a specified upper limit or until allocated assets are fully
        // utilized.
        (rsETHBurned, assetAmountUnlocked) = _unlockWithdrawalRequests(
            asset, params.totalAvailableAssets, params.rsETHPrice, params.assetPrice, firstExcludedIndex
        );

        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
```

**File:** contracts/LRTWithdrawalManager.sol (L846-850)
```text
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
```
