### Title
Unbounded Return Data in ETH Transfer to User-Controlled Address Causes Permanent Freezing of Withdrawal Funds - (File: `contracts/LRTWithdrawalManager.sol`)

### Summary
`LRTWithdrawalManager._transferAsset` uses a bare low-level `call` to send ETH to a user-controlled address without restricting the size of the return data. A recipient contract can return an arbitrarily large payload from its `receive()` function, causing the EVM to copy the entire return buffer into memory and exhaust all available gas, permanently reverting the withdrawal completion and freezing the user's funds in the contract.

### Finding Description
`_transferAsset` is the single ETH-transfer primitive used by both `_processWithdrawalCompletion` (called by `completeWithdrawal` and `completeWithdrawalForUser`) and `instantWithdrawal`:

```solidity
function _transferAsset(address asset, address to, uint256 amount) internal {
    if (asset == LRTConstants.ETH_TOKEN) {
        (bool sent,) = payable(to).call{ value: amount }("");
        if (!sent) revert EthTransferFailed();
    } else {
        IERC20(asset).safeTransfer(to, amount);
    }
}
```

In Solidity 0.8.x, even when the `bytes memory` return value is syntactically discarded with `(bool sent,)`, the compiler still emits `RETURNDATASIZE` / `RETURNDATACOPY` instructions that copy the entire return buffer into memory before the variable is dropped. A recipient contract whose `receive()` function returns a large blob (e.g., via inline assembly `return(0, largeSize)`) forces the EVM to allocate and copy that blob, consuming gas proportional to its size. With a sufficiently large payload the transaction always runs out of gas and reverts.

Because `_processWithdrawalCompletion` deletes the withdrawal request and decrements `unlockedWithdrawalsCount` only inside the same transaction, a revert rolls back all state changes. The withdrawal request remains in the queue but can never be executed — every subsequent attempt to call `completeWithdrawal` or `completeWithdrawalForUser` for that user/asset pair will hit the same gas bomb and revert. There is no admin escape hatch to force-finalize or cancel a stuck withdrawal request.

### Impact Explanation
A user whose withdrawal destination is a contract (e.g., a smart-contract wallet, a multisig, or a purpose-built attacker contract) can permanently freeze their own queued ETH withdrawal. Because the protocol provides no mechanism to override or cancel a stuck withdrawal, the ETH committed to that request is irrecoverable from the `LRTWithdrawalManager`. This satisfies the **Critical — Permanent freezing of funds** impact class.

### Likelihood Explanation
Any contract-based withdrawer can trigger this. Smart-contract wallets (Gnosis Safe, ERC-4337 accounts, etc.) are common in DeFi and may legitimately return non-empty data from `receive()`. A deliberate attacker can trivially deploy a contract that returns a large payload. The entry path (`initiateWithdrawal` → wait for unlock → `completeWithdrawal`) is fully permissionless and requires no special role.

### Recommendation
Replace the bare `call` in `_transferAsset` with an assembly-level call that caps the amount of return data copied into memory, analogous to the `ExcessivelySafeCall` pattern recommended in the reference report:

```solidity
// cap returndata copy to 0 bytes
assembly {
    success := call(gas(), to, amount, 0, 0, 0, 0)
}
```

Alternatively, forward only a fixed gas stipend (e.g., `call{value: amount, gas: 2300}`) to prevent the callee from executing arbitrary logic, though this may break contract wallets that require more gas in `receive()`.

### Proof of Concept
1. Deploy `MaliciousWallet`:
   ```solidity
   contract MaliciousWallet {
       receive() external payable {
           assembly { return(0, 1000000) } // return 1 MB of zeros
       }
   }
   ```
2. From `MaliciousWallet`, call `LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, amount, "")` after approving rsETH.
3. Wait for the operator to call `unlockQueue` for the ETH asset.
4. Call `completeWithdrawal(ETH_TOKEN, "")` (or have an operator call `completeWithdrawalForUser`).
5. The transaction reverts with out-of-gas every time because `_transferAsset` triggers `MaliciousWallet.receive()`, which forces the EVM to copy 1 MB of return data into memory.
6. The withdrawal request persists in the queue indefinitely; the ETH is permanently locked in `LRTWithdrawalManager`. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

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
