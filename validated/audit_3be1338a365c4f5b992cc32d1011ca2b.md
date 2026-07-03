### Title
`LRTConfig.setContract` Allows Replacing `LRT_UNSTAKING_VAULT` Without Checking Existing Funds, Temporarily Freezing User Withdrawals - (File: contracts/LRTConfig.sol)

---

### Summary
`LRTConfig._setContract` allows the admin to replace any contract address in `contractMap`, including `LRT_UNSTAKING_VAULT`, without verifying that the old vault holds no assets or has no pending withdrawal obligations. Because `LRTWithdrawalManager` resolves the vault address dynamically at call time, replacing the vault while assets are held there causes `unlockQueue()` to revert, permanently blocking withdrawal processing until the admin intervenes. Users' rsETH remains locked in the withdrawal manager with no path to completion.

---

### Finding Description

`LRTConfig._setContract` performs no state-safety check before overwriting a contract address:

```solidity
function _setContract(bytes32 key, address val) private {
    UtilLib.checkNonZeroAddress(val);
    if (contractMap[key] == val) {
        revert ValueAlreadyInUse();
    }
    contractMap[key] = val;
    emit SetContract(key, val);
}
``` [1](#0-0) 

`LRTWithdrawalManager.unlockQueue()` resolves the vault address dynamically on every call:

```solidity
ILRTUnstakingVault unstakingVault =
    ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
``` [2](#0-1) 

It then reads the vault's balance to determine how much can be unlocked:

```solidity
totalAvailableAssets: unstakingVault.balanceOf(asset)
``` [3](#0-2) 

If `totalAvailableAssets == 0` (because the new vault is empty), the function reverts immediately:

```solidity
if (params.totalAvailableAssets == 0) revert AmountMustBeGreaterThanZero();
``` [4](#0-3) 

Even if that check were bypassed, `unstakingVault.redeem()` would revert on the new empty vault when attempting to transfer assets:

```solidity
function redeem(address asset, uint256 amount) external nonReentrant onlyLRTWithdrawalManager {
    if (asset == LRTConstants.ETH_TOKEN) {
        ILRTWithdrawalManager(msg.sender).receiveFromLRTUnstakingVault{ value: amount }();
    } else {
        IERC20(asset).safeTransfer(msg.sender, amount);
    }
}
``` [5](#0-4) 

The assets deposited into the old vault via `transferAssetToLRTUnstakingVault` / `transferETHToLRTUnstakingVault` are now stranded with no protocol-level path to retrieve them through the normal withdrawal flow. [6](#0-5) 

**Contrast with the protected path**: `LRTConfig.updateAssetStrategy` explicitly checks that no NDC holds funds in the old strategy before allowing the update — demonstrating the protocol understands this class of risk but did not apply the same guard to `setContract`. [7](#0-6) 

---

### Impact Explanation

**Impact: Medium — Temporary freezing of funds.**

All users who have called `initiateWithdrawal()` have their rsETH locked inside `LRTWithdrawalManager`. The assets backing those withdrawals sit in the old `LRTUnstakingVault`. After the vault address is replaced, `unlockQueue()` reverts on every call, so no withdrawal request can ever be unlocked. Users cannot recover their rsETH until the admin either reverts the address change or manually migrates assets — neither of which is guaranteed to happen promptly. [8](#0-7) 

---

### Likelihood Explanation

**Likelihood: Low.**

The trigger is a legitimate admin action — replacing the unstaking vault during a contract upgrade — without first draining the old vault or completing pending withdrawals. The protocol already performs this kind of check for strategy updates (`updateAssetStrategy`), so the omission here is an oversight rather than intentional design. The scenario is realistic during any vault upgrade cycle.

---

### Recommendation

1. **Add a balance check in `setContract` for `LRT_UNSTAKING_VAULT`**: Before overwriting the address, verify that `ILRTUnstakingVault(oldVault).balanceOf(asset) == 0` for all supported assets.
2. **Alternatively**, mirror the pattern already used in `updateAssetStrategy`: revert if the old vault holds any non-negligible balance, forcing operators to drain it first.
3. **Or** implement a migration helper that atomically transfers all assets from the old vault to the new one before updating the pointer.

---

### Proof of Concept

1. Alice calls `LRTWithdrawalManager.initiateWithdrawal(stETH, rsETHAmount, "")`. Her rsETH is locked in the withdrawal manager; `assetsCommitted[stETH]` is incremented.
2. An operator calls `LRTDepositPool.transferAssetToLRTUnstakingVault(stETH, amount)`, moving stETH into the old `LRTUnstakingVault`.
3. Admin calls `LRTConfig.setContract(LRT_UNSTAKING_VAULT, newEmptyVault)`. No check is performed.
4. Operator calls `LRTWithdrawalManager.unlockQueue(stETH, ...)`. The function resolves `unstakingVault` to `newEmptyVault`, reads `balanceOf(stETH) == 0`, and reverts with `AmountMustBeGreaterThanZero`.
5. Alice's rsETH remains locked indefinitely. The stETH in the old vault is stranded with no protocol path to recover it through the withdrawal flow.

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

**File:** contracts/LRTConfig.sol (L244-251)
```text
    function _setContract(bytes32 key, address val) private {
        UtilLib.checkNonZeroAddress(val);
        if (contractMap[key] == val) {
            revert ValueAlreadyInUse();
        }
        contractMap[key] = val;
        emit SetContract(key, val);
    }
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

**File:** contracts/LRTWithdrawalManager.sol (L283-284)
```text
        ILRTOracle lrtOracle = ILRTOracle(lrtConfig.getContract(LRTConstants.LRT_ORACLE));
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
```

**File:** contracts/LRTWithdrawalManager.sol (L297-297)
```text
        if (params.totalAvailableAssets == 0) revert AmountMustBeGreaterThanZero();
```

**File:** contracts/LRTWithdrawalManager.sol (L849-849)
```text
            totalAvailableAssets: unstakingVault.balanceOf(asset)
```

**File:** contracts/LRTUnstakingVault.sol (L99-105)
```text
    function redeem(address asset, uint256 amount) external nonReentrant onlyLRTWithdrawalManager {
        if (asset == LRTConstants.ETH_TOKEN) {
            ILRTWithdrawalManager(msg.sender).receiveFromLRTUnstakingVault{ value: amount }();
        } else {
            IERC20(asset).safeTransfer(msg.sender, amount);
        }
    }
```

**File:** contracts/LRTDepositPool.sol (L240-265)
```text
    function transferAssetToLRTUnstakingVault(
        address asset,
        uint256 amount
    )
        external
        nonReentrant
        onlyAssetTransferRole
        onlySupportedERC20Token(asset)
    {
        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        IERC20(asset).safeTransfer(lrtUnstakingVault, amount);
    }

    /// @notice transfers ETH lying in this DepositPool to nLRTUnstakingVault contract
    /// @dev only callable by Asset Transfer Role
    /// @param amount ETH amount to transfer
    function transferETHToLRTUnstakingVault(uint256 amount)
        external
        nonReentrant
        onlyAssetTransferRole
        onlySupportedAsset(LRTConstants.ETH_TOKEN)
    {
        address lrtUnstakingVault = lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT);
        ILRTUnstakingVault(lrtUnstakingVault).receiveFromLRTDepositPool{ value: amount }();
        emit EthTransferred(lrtUnstakingVault, amount);
    }
```
