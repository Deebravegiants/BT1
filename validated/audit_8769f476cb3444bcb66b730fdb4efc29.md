### Title
`instantWithdrawal` Bypasses `assetsCommitted` Solvency Constraint via Structurally Decoupled `queuedWithdrawalsBuffer`, Enabling Drain of Assets Reserved for Queued Withdrawals - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`LRTWithdrawalManager.instantWithdrawal()` enforces a different and structurally decoupled availability constraint than `initiateWithdrawal()`. Queued withdrawals commit assets via `assetsCommitted[asset]`, but instant withdrawals bypass this entirely and only check `queuedWithdrawalsBuffer[asset]` in `LRTUnstakingVault`, which defaults to `0` and is never automatically synchronized with `assetsCommitted`. Any rsETH holder can drain the `LRTUnstakingVault` of assets already committed to queued withdrawers, causing those queued withdrawals to be temporarily frozen.

---

### Finding Description

`initiateWithdrawal()` enforces a hard cap on over-commitment:

```solidity
if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();
assetsCommitted[asset] += expectedAssetAmount;
```

`getAvailableAssetAmount` computes `totalAssets - assetsCommitted[asset]`, where `totalAssets` is the full protocol TVL across the deposit pool, NDCs, EigenLayer, and the unstaking vault. [1](#0-0) [2](#0-1) 

`instantWithdrawal()` does **not** check `assetsCommitted` at all. It only checks `getAssetsAvailableForInstantWithdrawal`, which is `vaultBalance - queuedWithdrawalsBuffer[asset]`:

```solidity
if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
    revert CantInstantWithdrawMoreThanAvailable();
}
unstakingVault.redeem(asset, assetAmountUnlocked);
``` [3](#0-2) 

`queuedWithdrawalsBuffer` is a mapping that defaults to `0` and is set manually by an operator via `setQueuedWithdrawalsBuffer`. It is **never automatically updated** when `assetsCommitted` grows:

```solidity
mapping(address asset => uint256 buffer) public queuedWithdrawalsBuffer;
``` [4](#0-3) [5](#0-4) [6](#0-5) 

The two constraints are structurally decoupled:

| Path | Constraint checked | Updated automatically? |
|---|---|---|
| `initiateWithdrawal` | `assetsCommitted[asset]` | Yes, on every queued request |
| `instantWithdrawal` | `queuedWithdrawalsBuffer[asset]` | **No** — operator-only, defaults to 0 |

**Attack scenario:**

1. Operator unstakes 100 ETH from EigenLayer into `LRTUnstakingVault` to service pending queued withdrawals.
2. User A calls `initiateWithdrawal(ETH, ...)` for 100 ETH. `assetsCommitted[ETH] += 100`. User A's rsETH is now locked in the withdrawal manager.
3. `queuedWithdrawalsBuffer[ETH]` is `0` (default, never set by operator).
4. User B calls `instantWithdrawal(ETH, ...)` for 100 ETH. `getAssetsAvailableForInstantWithdrawal` returns `100 - 0 = 100`. The check passes. The vault is drained.
5. `unlockQueue` now reverts with `AmountMustBeGreaterThanZero` because `unstakingVault.balanceOf(ETH) == 0`.
6. User A's rsETH is locked in the withdrawal manager with no path to claim until the operator manually refills the vault by unstaking more ETH from EigenLayer.

This is the structural analog to the external report: `instantWithdrawal` is the path that explicitly bypasses the `assetsCommitted` solvency constraint, just as `SharesCooldown.finalize()` bypassed `minimumJrtSrtRatio`. [7](#0-6) 

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

Queued withdrawal users have their rsETH locked in `LRTWithdrawalManager` with no cancel mechanism visible in the contract. They cannot claim their underlying assets until an operator manually unstakes additional ETH from EigenLayer and refills the vault. The freeze is not permanent (the protocol retains assets in EigenLayer), but it is indefinite from the user's perspective and requires privileged operator action to resolve. [8](#0-7) 

---

### Likelihood Explanation

**Medium-High.** The `queuedWithdrawalsBuffer` defaults to `0` for every asset. Instant withdrawal is enabled per-asset by the manager (`setInstantWithdrawalEnabled`). Once enabled, any rsETH holder can call `instantWithdrawal` at any time. No coordination or privileged access is required for the attacker. The only mitigation is the operator proactively setting `queuedWithdrawalsBuffer` to match `assetsCommitted`, but there is no on-chain enforcement of this and no event or mechanism that triggers a buffer update when `assetsCommitted` changes. [9](#0-8) [10](#0-9) 

---

### Recommendation

Automatically synchronize `queuedWithdrawalsBuffer` with `assetsCommitted` on every call to `initiateWithdrawal`. Specifically, when a queued withdrawal is added, increase `queuedWithdrawalsBuffer[asset]` by `expectedAssetAmount` in `LRTUnstakingVault`, and decrease it when the withdrawal is unlocked or cancelled. This ensures the buffer always reflects the actual committed liability, removing the structural decoupling that allows instant withdrawals to drain reserved assets.

Alternatively, modify `instantWithdrawal` to also check that `assetAmountUnlocked` does not exceed `unstakingVault.balanceOf(asset) - assetsCommitted[asset]` (i.e., the same constraint used by `getAvailableAssetAmount` but scoped to vault-held assets only).

---

### Proof of Concept

```solidity
// Preconditions:
// - instantWithdrawal is enabled for ETH
// - queuedWithdrawalsBuffer[ETH] == 0 (default)
// - LRTUnstakingVault holds 100 ETH (recently unstaked from EigenLayer)

// Step 1: UserA initiates a queued withdrawal
vm.prank(userA);
withdrawalManager.initiateWithdrawal(ETH, rsETHAmount_100ETH, "");
// assetsCommitted[ETH] == 100 ETH
// userA's rsETH is now locked in withdrawalManager

// Step 2: UserB drains the vault via instantWithdrawal
// getAssetsAvailableForInstantWithdrawal returns 100 - 0 = 100 ETH
vm.prank(userB);
withdrawalManager.instantWithdrawal(ETH, rsETHAmount_100ETH, "");
// LRTUnstakingVault.balanceOf(ETH) == 0

// Step 3: Operator tries to unlock the queue for userA
// unlockQueue reads unstakingVault.balanceOf(ETH) == 0
// Reverts with AmountMustBeGreaterThanZero
vm.prank(operator);
withdrawalManager.unlockQueue(ETH, type(uint256).max, ...);
// REVERTS — userA's funds are frozen indefinitely
``` [11](#0-10) [12](#0-11)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L55-56)
```text
    mapping(address asset => bool) public isInstantWithdrawalEnabled;
    uint256 public instantWithdrawalFee; // Fee in basis points (1 = 0.01%)
```

**File:** contracts/LRTWithdrawalManager.sol (L170-173)
```text
        if (expectedAssetAmount > getAvailableAssetAmount(asset)) revert ExceedAmountToWithdraw();

        // preventing over-withdrawal.
        assetsCommitted[asset] += expectedAssetAmount;
```

**File:** contracts/LRTWithdrawalManager.sol (L212-235)
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
        if (rsETHUnstaked == 0 || rsETHUnstaked < minRsEthAmountToWithdraw[asset]) {
            revert InvalidAmountToWithdraw();
        }
        if (IERC20(lrtConfig.rsETH()).balanceOf(msg.sender) < rsETHUnstaked) revert NotEnoughRsETH();
        uint256 assetAmountUnlocked = getExpectedAssetAmount(asset, rsETHUnstaked);
        IRSETH(lrtConfig.rsETH()).burnFrom(address(msg.sender), rsETHUnstaked);
        ILRTUnstakingVault unstakingVault = ILRTUnstakingVault(lrtConfig.getContract(LRTConstants.LRT_UNSTAKING_VAULT));
        if (assetAmountUnlocked > unstakingVault.getAssetsAvailableForInstantWithdrawal(asset)) {
            revert CantInstantWithdrawMoreThanAvailable();
        }

        unstakingVault.redeem(asset, assetAmountUnlocked);
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

**File:** contracts/LRTWithdrawalManager.sol (L360-367)
```text
    function setInstantWithdrawalEnabled(address asset, bool enabled)
        external
        onlySupportedAsset(asset)
        onlyLRTManager
    {
        isInstantWithdrawalEnabled[asset] = enabled;
        emit InstantWithdrawalEnabledUpdated(asset, enabled);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L599-603)
```text
    function getAvailableAssetAmount(address asset) public view override returns (uint256 availableAssetAmount) {
        ILRTDepositPool lrtDepositPool = ILRTDepositPool(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        uint256 totalAssets = lrtDepositPool.getTotalAssetDeposits(asset);
        availableAssetAmount = totalAssets > assetsCommitted[asset] ? totalAssets - assetsCommitted[asset] : 0;
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L699-738)
```text
    function _processWithdrawalCompletion(address asset, address user, string calldata referralId) internal {
        if (userAssociatedNonces[asset][user].empty()) {
            revert NoWithdrawalRequests(user, asset);
        }

        // Retrieve and remove the oldest withdrawal request for the user.
        uint256 usersFirstWithdrawalRequestNonce = userAssociatedNonces[asset][user].popFront();
        // Ensure the request is already unlocked.
        if (usersFirstWithdrawalRequestNonce >= nextLockedNonce[asset]) revert WithdrawalLocked();

        bytes32 requestId = getRequestId(asset, usersFirstWithdrawalRequestNonce);
        WithdrawalRequest memory request = withdrawalRequests[requestId];

        delete withdrawalRequests[requestId];

        // Check that the withdrawal delay has passed since the request's initiation.
        if (block.number < request.withdrawalStartBlock + withdrawalDelayBlocks) revert WithdrawalDelayNotPassed();

        unlockedWithdrawalsCount[asset]--;

        // If Aave integration is enabled and asset is ETH, withdraw from Aave if needed
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN) {
            uint256 contractBalance = address(this).balance;
            if (contractBalance < request.expectedAssetAmount) {
                uint256 amountNeeded = request.expectedAssetAmount - contractBalance;
                _withdrawFromAave(amountNeeded);

                // Verify we have sufficient balance after withdrawal
                uint256 balanceAfter = address(this).balance;
                if (balanceAfter < request.expectedAssetAmount) {
                    revert InsufficientLiquidityForWithdrawal();
                }
            }
        }

        _transferAsset(asset, user, request.expectedAssetAmount);

        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(user, asset, request.rsETHUnstaked, request.expectedAssetAmount);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L837-851)
```text
    function _createUnlockParams(
        ILRTOracle lrtOracle,
        ILRTUnstakingVault unstakingVault,
        address asset
    )
        internal
        view
        returns (UnlockParams memory)
    {
        return UnlockParams({
            rsETHPrice: lrtOracle.rsETHPrice(),
            assetPrice: lrtOracle.getAssetPrice(asset),
            totalAvailableAssets: unstakingVault.balanceOf(asset)
        });
    }
```

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

**File:** contracts/LRTUnstakingVault.sol (L229-237)
```text
    function getAssetsAvailableForInstantWithdrawal(address asset)
        external
        view
        onlySupportedAsset(asset)
        returns (uint256 availableAmount)
    {
        uint256 vaultBalance = balanceOf(asset);
        uint256 reservedBuffer = queuedWithdrawalsBuffer[asset];
        availableAmount = reservedBuffer >= vaultBalance ? 0 : vaultBalance - reservedBuffer;
```
