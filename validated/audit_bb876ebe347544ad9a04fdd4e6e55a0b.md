### Title
ETH Withdrawal Permanently Frozen When Withdrawing User Address Cannot Receive ETH - (File: contracts/LRTWithdrawalManager.sol)

### Summary
`LRTWithdrawalManager._transferAsset` sends ETH to the withdrawing user via a low-level `.call{value:}` and reverts the entire transaction on failure. When the user is a smart contract without a payable `receive()` function (or one that deliberately reverts), every call to `completeWithdrawal` or `completeWithdrawalForUser` will revert permanently. Because there is no cancellation path and no alternative recipient mechanism, the user's ETH is frozen inside `LRTWithdrawalManager` indefinitely.

### Finding Description

`_processWithdrawalCompletion` is the shared internal function called by both `completeWithdrawal` (user-initiated) and `completeWithdrawalForUser` (operator-initiated). Its final step is:

```solidity
_transferAsset(asset, user, request.expectedAssetAmount);
```

`_transferAsset` for ETH is:

```solidity
function _transferAsset(address asset, address to, uint256 amount) internal {
    if (asset == LRTConstants.ETH_TOKEN) {
        (bool sent,) = payable(to).call{ value: amount }("");
        if (!sent) revert EthTransferFailed();   // <-- hard revert
    } else {
        IERC20(asset).safeTransfer(to, amount);
    }
}
``` [1](#0-0) 

If `to` is a contract that cannot receive ETH, the call returns `false` and `EthTransferFailed` is thrown. Because Solidity reverts the entire transaction, the earlier state mutations (`popFront`, `delete withdrawalRequests[requestId]`, `unlockedWithdrawalsCount[asset]--`) are also rolled back, leaving the request permanently in the unlocked queue. [2](#0-1) 

The ETH itself was already transferred from `LRTUnstakingVault` into `LRTWithdrawalManager` during `unlockQueue` via `unstakingVault.redeem(asset, assetAmountUnlocked)`. It sits in the withdrawal manager with no way out:

- `completeWithdrawal` / `completeWithdrawalForUser` will always revert for this user.
- `sweepRemainingAssets` requires `hasUnlockedWithdrawals(asset) == false`, which can never be satisfied while the stuck request remains counted. [3](#0-2) 

There is no `cancelWithdrawal` function and no mechanism to redirect the payout to a different address.

### Impact Explanation

**Critical — Permanent freezing of funds.**

Once the withdrawal is unlocked and the ETH is redeemed from the unstaking vault into `LRTWithdrawalManager`, the ETH is irrecoverable for any user whose address cannot accept ETH. The rsETH was already burned in `unlockQueue` (`IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned)`), so the user loses both their rsETH and the corresponding ETH. [4](#0-3) 

### Likelihood Explanation

**Medium.**

Any smart-contract account that holds rsETH and calls `initiateWithdrawal` is at risk: DeFi protocols, multisigs with non-standard `receive()` logic, proxy contracts whose implementation does not forward ETH, or any contract that deliberately or accidentally reverts in its fallback. The protocol explicitly supports contract callers — `completeWithdrawalForUser` exists precisely because operators may need to complete withdrawals on behalf of contracts — yet the operator path suffers the same revert. [5](#0-4) 

The developer comment on `completeWithdrawalForUser` ("Not expected to be used for ETH; potential gas grief scenarios are non-impactful for ETH") shows awareness of ETH-transfer edge cases but incorrectly dismisses the permanent-freeze scenario.

### Recommendation

Replace the push-payment pattern with a **pull-payment** (withdrawal pattern):

1. Instead of calling `_transferAsset(asset, user, amount)` inside `_processWithdrawalCompletion`, credit a `claimable[user][asset]` mapping.
2. Add a separate `claimAsset(address asset)` function that the user calls to pull their ETH.

Alternatively, add a `cancelWithdrawal` function that allows a user to reclaim their rsETH before the request is unlocked, and ensure that after unlocking, an admin/operator can redirect a stuck ETH payout to a user-specified rescue address.

### Proof of Concept

1. Deploy a contract `MaliciousReceiver` with a reverting `receive()`:
   ```solidity
   contract MaliciousReceiver {
       ILRTWithdrawalManager wm;
       IRSETH rsETH;
       constructor(address _wm, address _rsETH) { wm = ILRTWithdrawalManager(_wm); rsETH = IRSETH(_rsETH); }
       function doWithdraw(uint256 amount) external {
           rsETH.approve(address(wm), amount);
           wm.initiateWithdrawal(ETH_TOKEN, amount, "");
       }
       receive() external payable { revert(); }
   }
   ```
2. Call `doWithdraw` — rsETH is transferred to `LRTWithdrawalManager`.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)` — rsETH is burned, ETH is redeemed into `LRTWithdrawalManager`.
4. Call `wm.completeWithdrawal(ETH_TOKEN, "")` from `MaliciousReceiver` — reverts with `EthTransferFailed`.
5. Operator calls `wm.completeWithdrawalForUser(ETH_TOKEN, address(MaliciousReceiver), "")` — also reverts.
6. ETH remains permanently locked in `LRTWithdrawalManager`; `sweepRemainingAssets` is also blocked because `unlockedWithdrawalsCount[ETH_TOKEN] > 0`. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTWithdrawalManager.sol (L183-185)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L192-204)
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
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L268-320)
```text
    function unlockQueue(
        address asset,
        uint256 firstExcludedIndex,
        uint256 minimumAssetPrice,
        uint256 minimumRsEthPrice,
        uint256 maximumAssetPrice,
        uint256 maximumRsEthPrice
    )
        external
        nonReentrant
        onlySupportedAsset(asset)
        whenNotPaused
        onlyAssetTransferOrOperatorRole
        returns (uint256 rsETHBurned, uint256 assetAmountUnlocked)
    {
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

        // If Aave integration is enabled and asset is ETH, deposit to Aave
        if (isAaveIntegrationEnabled && asset == LRTConstants.ETH_TOKEN && assetAmountUnlocked > 0) {
            try this.depositToAaveExternal(assetAmountUnlocked) { }
            catch (bytes memory reason) {
                emit AaveDepositFailed(assetAmountUnlocked, reason);
                // Silently fail if Aave deposit fails (e.g., pool at max capacity)
                // Funds remain in contract for withdrawals
            }
        }

        emit AssetUnlocked(asset, rsETHBurned, assetAmountUnlocked, params.rsETHPrice, params.assetPrice);
    }
```

**File:** contracts/LRTWithdrawalManager.sol (L395-413)
```text
    function sweepRemainingAssets(address asset)
        external
        nonReentrant
        onlySupportedAsset(asset)
        onlyLRTManager
        returns (uint256 transferredAmount)
    {
        // Check that all withdrawals are completed
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();

        uint256 balance = _getAssetBalance(asset);
        if (balance == 0) revert AmountMustBeGreaterThanZero();

        // Transfer to treasury
        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        _transferAsset(asset, treasury, balance);

        emit RemainingAssetsSwept(asset, balance, treasury);
        return balance;
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
