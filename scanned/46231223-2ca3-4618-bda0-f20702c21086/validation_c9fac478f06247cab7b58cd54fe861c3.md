### Title
User Can Escape rsETH Fund Seizure by Front-Running `blockUserTransfers` with `initiateWithdrawal` or `instantWithdrawal` — (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`RSETH.sol` implements a fund-seizure mechanism via `blockUserTransfers` + `recoverFrozenFunds`. However, `LRTWithdrawalManager.initiateWithdrawal` and `instantWithdrawal` allow a user to drain their rsETH balance before the block is applied, leaving `recoverFrozenFunds` with nothing to recover.

---

### Finding Description

`RSETH.sol` provides two admin-facing functions for seizing rsETH from a malicious user:

1. `blockUserTransfers(address[] accounts)` — sets `transfersBlockedUntil[account] = block.timestamp + 1 days`, blocking all rsETH transfers to/from the account for 24 hours.
2. `recoverFrozenFunds(address from)` — transfers the **current rsETH balance** of the blocked address to `custodyAddress`. [1](#0-0) [2](#0-1) 

The enforcement hook in `_transfer` checks both sender and receiver: [3](#0-2) 

However, `LRTWithdrawalManager.initiateWithdrawal` moves rsETH from the user's wallet into the `LRTWithdrawalManager` contract via `safeTransferFrom`: [4](#0-3) 

And `instantWithdrawal` burns rsETH directly from the user via `burnFrom`, which also calls `_enforceNotBlocked`: [5](#0-4) 

Neither `initiateWithdrawal` nor `instantWithdrawal` contains any check for whether the caller is currently blocked or is about to be blocked. The `blockUserTransfers` call and the withdrawal initiation are two separate transactions with no atomicity guarantee.

Critically, `completeWithdrawal` transfers ETH or LST (not rsETH) to the user, so it is **not** gated by `_enforceNotBlocked`: [6](#0-5) 

---

### Impact Explanation

A user who anticipates being blocked (e.g., they observe a `blockUserTransfers` transaction in the mempool, or they proactively act knowing they have behaved maliciously) can:

1. Call `initiateWithdrawal` — rsETH is transferred from their wallet to `LRTWithdrawalManager`. Their rsETH balance drops to zero.
2. `blockUserTransfers` executes — but the user's rsETH balance is now zero.
3. `recoverFrozenFunds` is called — recovers zero rsETH.
4. After the withdrawal delay, the user calls `completeWithdrawal` and receives ETH/LST back.

Alternatively, via `instantWithdrawal`, the user can burn rsETH and receive ETH/LST in a single transaction before the block is applied.

The protocol's fund-seizure mechanism is rendered completely ineffective. The malicious user escapes with full value. This maps to **Low — Contract fails to deliver promised returns** (the `blockUserTransfers` + `recoverFrozenFunds` security guarantee is not upheld), with potential escalation to **Medium** if the protocol relies on this mechanism as a primary defense against malicious actors.

---

### Likelihood Explanation

The attack does not require sophisticated tooling. Any user who:
- Monitors the mempool for `blockUserTransfers` transactions targeting their address, or
- Proactively moves funds when they know they have acted maliciously

can execute this escape. The withdrawal path is a standard user-facing function with no special permissions required.

---

### Recommendation

Add a check in `initiateWithdrawal` and `instantWithdrawal` that reverts if the caller is currently blocked in `RSETH`:

```solidity
function initiateWithdrawal(...) external ... {
    // Add at the top:
    IRSETH(lrtConfig.rsETH()).enforceNotBlocked(msg.sender);
    ...
}
```

Expose `_enforceNotBlocked` as a public/external view function in `RSETH.sol`, or add a `isBlocked(address)` view that `LRTWithdrawalManager` can call before processing any withdrawal initiation. This mirrors the fix suggested in the Ethos Network report: add a check at the withdrawal entry point that prevents action when the user is in a penalized/blocked state.

---

### Proof of Concept

1. Manager identifies malicious user `Alice` and prepares a `blockUserTransfers([Alice])` transaction.
2. Alice observes this in the mempool and front-runs with `LRTWithdrawalManager.initiateWithdrawal(stETH, aliceRsETHBalance, "")`.
   - `safeTransferFrom` moves all of Alice's rsETH to `LRTWithdrawalManager`. Alice's rsETH balance = 0.
3. `blockUserTransfers([Alice])` executes. `transfersBlockedUntil[Alice] = block.timestamp + 1 days`.
4. Admin calls `recoverFrozenFunds(Alice)`. `balanceOf(Alice) == 0`. Zero rsETH is recovered.
5. After `withdrawalDelayBlocks` pass, operator calls `unlockQueue` — rsETH is burned from `LRTWithdrawalManager`, withdrawal is unlocked.
6. Alice calls `completeWithdrawal(stETH, "")`. `_transferAsset` sends stETH to Alice. No rsETH transfer occurs; `_enforceNotBlocked` is never triggered.
7. Alice has successfully converted her rsETH to stETH, bypassing the seizure mechanism entirely. [7](#0-6) [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/RSETH.sol (L161-177)
```text
    function blockUserTransfers(address[] calldata accounts) external onlyLRTManager {
        uint256 blockedUntil = block.timestamp + 1 days;
        uint256 length = accounts.length;

        for (uint256 i = 0; i < length; ++i) {
            address account = accounts[i];

            if (isPermanentlyExempt[account] || account == address(0)) continue;

            uint256 prevBlockedUntil = transfersBlockedUntil[account];

            if (blockedUntil != prevBlockedUntil) {
                transfersBlockedUntil[account] = blockedUntil;
                emit UserTransfersBlocked(account, blockedUntil);
            }
        }
    }
```

**File:** contracts/RSETH.sol (L206-219)
```text
    function recoverFrozenFunds(address from) external onlyLRTAdmin {
        UtilLib.checkNonZeroAddress(from);
        UtilLib.checkNonZeroAddress(custodyAddress);

        if (isPermanentlyExempt[from]) revert AddressPermanentlyExempt(from);

        uint256 blockedUntil = transfersBlockedUntil[from];
        if (blockedUntil == 0 || block.timestamp >= blockedUntil) revert NoActiveTransferBlock(from);

        uint256 accountBalance = balanceOf(from);

        // Bypass transfer block enforcement when transferring to custody address
        super._transfer(from, custodyAddress, accountBalance);
        emit FrozenFundsRecovered(from, custodyAddress, accountBalance);
```

**File:** contracts/RSETH.sol (L287-306)
```text
    function _transfer(address from, address to, uint256 amount) internal override {
        _enforceNotBlocked(from);
        _enforceNotBlocked(to);
        super._transfer(from, to, amount);
    }

    /// @dev Reverts if `account` is currently blocked (used for transfers, mints, and burns)
    function _enforceNotBlocked(address account) internal {
        // Addresses that are permanently exempt can never be blocked
        if (isPermanentlyExempt[account]) return;

        // Check if the account has an active transfer block
        uint256 blockedUntil = transfersBlockedUntil[account];
        if (blockedUntil == 0) return;

        if (block.timestamp < blockedUntil) revert TransfersBlocked(account, blockedUntil);

        // Auto-clean up expired block
        delete transfersBlockedUntil[account];
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

**File:** contracts/LRTWithdrawalManager.sol (L182-185)
```text
    /// @param asset The asset address the user wishes to withdraw.
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L212-253)
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

        uint256 fee = (assetAmountUnlocked * instantWithdrawalFee) / 10_000;
        uint256 userAmount = assetAmountUnlocked - fee;

        address feeRecipient = instantWithdrawalFeeRecipient;
        if (feeRecipient == address(0)) {
            // Backwards-compatible default: send fees to the protocol treasury
            feeRecipient = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        }
        if (fee > 0) {
            _transferAsset(asset, feeRecipient, fee);
            emit InstantWithdrawalFeeCollected(msg.sender, asset, fee);
        }

        _transferAsset(asset, msg.sender, userAmount);
        emit ReferralIdEmitted(referralId);
        emit AssetWithdrawalFinalized(msg.sender, asset, rsETHUnstaked, userAmount);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L699-737)
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
```
