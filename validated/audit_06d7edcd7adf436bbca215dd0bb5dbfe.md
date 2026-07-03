### Title
LST Token Blocklist or Pause Permanently Freezes User Funds After rsETH Is Burned in Withdrawal Queue - (File: contracts/LRTWithdrawalManager.sol)

### Summary

`LRTWithdrawalManager` processes withdrawals across three separate transactions. After a user's rsETH is irreversibly burned in `unlockQueue`, a subsequent blocklist or pause on the LST token (e.g., stETH) prevents `completeWithdrawal` from delivering the owed LST, permanently freezing the user's funds with no recovery path.

### Finding Description

The withdrawal lifecycle in `LRTWithdrawalManager` is split across three independent transactions:

1. **`initiateWithdrawal`** — User transfers rsETH to the contract; the request is queued under `userAssociatedNonces[asset][msg.sender]`.
2. **`unlockQueue`** (operator) — rsETH held by the contract is burned via `burnFrom(address(this), rsETHBurned)`, and the corresponding LST amount is pulled from `LRTUnstakingVault` into the withdrawal manager.
3. **`completeWithdrawal`** / **`completeWithdrawalForUser`** — Calls `_processWithdrawalCompletion`, which calls `_transferAsset(asset, user, request.expectedAssetAmount)`. [1](#0-0) 

`_transferAsset` for ERC20 assets calls `IERC20(asset).safeTransfer(to, amount)`: [2](#0-1) 

If the LST token (stETH, ETHx, or sfrxETH) blocklists the user's address or pauses transfers between step 2 and step 3, `safeTransfer` reverts. Because the rsETH was already burned in step 2 (a separate, already-finalized transaction), the revert in step 3 does **not** restore the burned rsETH. The user has permanently surrendered their rsETH and receives nothing.

The `WithdrawalRequest` struct stores no recipient address — only `rsETHUnstaked`, `expectedAssetAmount`, and `withdrawalStartBlock`: [3](#0-2) 

The recipient is always `user` (the original depositor's address), looked up via `userAssociatedNonces`. There is no mechanism to redirect the payout to an alternative address. Even `completeWithdrawalForUser` (operator path) still sends to the same `user`: [4](#0-3) 

stETH (Lido) maintains an OFAC-compliance blocklist that permanently prevents transfers to/from sanctioned addresses. ETHx and sfrxETH have pausable transfer mechanisms. All three are supported withdrawal assets in this protocol.

### Impact Explanation

Once `unlockQueue` burns the user's rsETH, the user's claim is represented solely by the LST balance held in `LRTWithdrawalManager`. If the LST token subsequently blocklists the user or pauses transfers:

- **Permanent blocklist (stETH)**: The user's LST is permanently undeliverable. rsETH is already burned. The user suffers a total, permanent loss of their principal — **permanent freezing of funds (Critical)**.
- **Temporary pause**: The user cannot complete withdrawal until the pause lifts — **temporary freezing of funds (Medium)**.

There is no admin escape hatch: no function exists to redirect a pending withdrawal to a different recipient address, and the `WithdrawalRequest` struct contains no recipient field to update.

### Likelihood Explanation

stETH's OFAC blocklist is active on mainnet and has been applied to real addresses. A user who deposits stETH-backed rsETH and later becomes sanctioned faces this scenario. The protocol explicitly supports stETH as a withdrawal asset (initialized in `initialize2`): [5](#0-4) 

The multi-transaction withdrawal design (8-day delay by default) creates a wide window between rsETH burn and LST delivery during which a blocklist can be applied. Likelihood is low-to-medium for the permanent case, medium for the pause case.

### Recommendation

1. **Two-step payout separation**: Do not burn rsETH in `unlockQueue` atomically with asset allocation. Instead, burn rsETH only at `completeWithdrawal` time, so a failed LST transfer reverts the entire operation and the user retains their rsETH.
2. **Alternative recipient**: Allow users to designate an alternative recipient address for their withdrawal payout before `completeWithdrawal` is called, so a blocklisted address can redirect funds.
3. **Rescue path**: Add an admin function to redirect a stuck withdrawal's payout to a different address (e.g., a custody address), analogous to the `recoverFrozenFunds` mechanism already present in `RSETH.sol`. [6](#0-5) 

### Proof of Concept

1. User calls `initiateWithdrawal(stETH, 10e18, "")`. rsETH is transferred to `LRTWithdrawalManager`; request is queued.
2. Operator calls `unlockQueue(stETH, ...)`. rsETH is burned from the contract; stETH is pulled from `LRTUnstakingVault` into `LRTWithdrawalManager`.
3. stETH's OFAC blocklist is applied to the user's address (e.g., due to regulatory action).
4. User calls `completeWithdrawal(stETH, "")`. `_processWithdrawalCompletion` calls `_transferAsset(stETH, user, amount)`, which calls `stETH.safeTransfer(user, amount)`. stETH reverts because `user` is blocklisted.
5. Operator calls `completeWithdrawalForUser(stETH, user, "")`. Same revert — the recipient is still `user`.
6. User's rsETH is permanently burned. The stETH sits in `LRTWithdrawalManager` with no mechanism to redirect it. Funds are permanently frozen. [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L118-120)
```text
        unlockedWithdrawalsCount[lrtConfig.getLSTToken(LRTConstants.ST_ETH_TOKEN)] = unlockedWithdrawalsCountSTETH;
        unlockedWithdrawalsCount[lrtConfig.getLSTToken(LRTConstants.ETHX_TOKEN)] = unlockedWithdrawalsCountETHx;
        unlockedWithdrawalsCount[LRTConstants.ETH_TOKEN] = unlockedWithdrawalsCountETH;
```

**File:** contracts/LRTWithdrawalManager.sol (L192-203)
```text
    function completeWithdrawalForUser(
        address asset,
        address user,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlyLRTOperator
    {
        _processWithdrawalCompletion(asset, user, referralId);
        emit AssetWithdrawalCompletedBy(msg.sender);
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

**File:** contracts/LRTWithdrawalManager.sol (L751-753)
```text
        withdrawalRequests[requestId] = WithdrawalRequest({
            rsETHUnstaked: rsETHUnstaked, expectedAssetAmount: expectedAssetAmount, withdrawalStartBlock: block.number
        });
```

**File:** contracts/LRTWithdrawalManager.sol (L876-883)
```text
    function _transferAsset(address asset, address to, uint256 amount) internal {
        if (asset == LRTConstants.ETH_TOKEN) {
            (bool sent,) = payable(to).call{ value: amount }("");
            if (!sent) revert EthTransferFailed();
        } else {
            IERC20(asset).safeTransfer(to, amount);
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
