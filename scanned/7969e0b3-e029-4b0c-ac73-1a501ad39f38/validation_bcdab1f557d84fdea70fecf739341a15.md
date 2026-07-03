### Title
DoS: ETH-rejecting or blacklisted withdrawer permanently blocks `sweepRemainingAssets()` - (File: contracts/LRTWithdrawalManager.sol)

### Summary

`sweepRemainingAssets()` requires `unlockedWithdrawalsCount[asset] == 0` before sweeping leftover assets to the treasury. The counter is only decremented inside `_processWithdrawalCompletion()`, which calls `_transferAsset()` to push funds to the user. If that push transfer fails (ETH recipient reverts, or LST recipient is blacklisted), the entire transaction reverts, the counter never decrements, and `sweepRemainingAssets()` is permanently blocked.

---

### Finding Description

`sweepRemainingAssets()` enforces a hard gate:

```solidity
if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();
``` [1](#0-0) 

`hasUnlockedWithdrawals` simply checks:

```solidity
return unlockedWithdrawalsCount[asset] > 0;
``` [2](#0-1) 

`unlockedWithdrawalsCount[asset]` is incremented in `_unlockWithdrawalRequests()` (called by `unlockQueue`) and decremented only inside `_processWithdrawalCompletion()`:

```solidity
unlockedWithdrawalsCount[asset]--;
...
_transferAsset(asset, user, request.expectedAssetAmount);
``` [3](#0-2) 

`_transferAsset` for ETH uses a raw `call` that reverts on failure:

```solidity
(bool sent,) = payable(to).call{ value: amount }("");
if (!sent) revert EthTransferFailed();
``` [4](#0-3) 

For ERC20 LSTs it uses `safeTransfer`, which reverts if the recipient is blacklisted or the token is paused:

```solidity
IERC20(asset).safeTransfer(to, amount);
``` [5](#0-4) 

Because `unlockedWithdrawalsCount[asset]--` and `delete withdrawalRequests[requestId]` both appear **before** `_transferAsset`, a revert in `_transferAsset` rolls back all state changes. The request is never deleted, the counter never decrements, and no admin escape hatch exists to manually clear a stuck entry.

The operator-callable `completeWithdrawalForUser` routes through the same `_processWithdrawalCompletion` path and therefore suffers the same failure:

```solidity
function completeWithdrawalForUser(...) external ... onlyLRTOperator {
    _processWithdrawalCompletion(asset, user, referralId);
``` [6](#0-5) 

---

### Impact Explanation

After `unlockQueue` runs, rsETH is already burned from the contract and the underlying asset is already redeemed from the unstaking vault into `LRTWithdrawalManager`:

```solidity
if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
unstakingVault.redeem(asset, assetAmountUnlocked);
``` [7](#0-6) 

If the transfer to the user then permanently fails:

1. The user's rsETH is burned with no recourse — their asset amount is permanently frozen inside `LRTWithdrawalManager`.
2. `unlockedWithdrawalsCount[asset]` stays `> 0` forever.
3. `sweepRemainingAssets()` is permanently blocked for that asset, freezing any excess balance that should flow to the treasury.

Impact: **Critical — permanent freezing of user funds** and **permanent freezing of unclaimed yield** (treasury sweep).

---

### Likelihood Explanation

**ETH path (deliberate attack):** An attacker deploys a contract with no `receive()` or a reverting fallback, calls `initiateWithdrawal` for ETH with a minimal rsETH amount, waits for the operator to call `unlockQueue`, and the withdrawal is permanently stuck. Cost is negligible (gas + `minRsEthAmountToWithdraw`).

**LST path (accidental or deliberate):** A user whose address is later blacklisted by a supported LST (e.g., a token with a compliance blacklist) will have their unlocked withdrawal permanently stuck with no admin remedy.

Both scenarios are realistic and externally triggerable by an unprivileged depositor.

---

### Recommendation

1. **Add an admin rescue function** that can forcibly delete a stuck withdrawal request and decrement `unlockedWithdrawalsCount[asset]`, sending the asset to a treasury address instead of the original user.
2. **Alternatively**, wrap `_transferAsset` in a try/catch (or use a low-level call that does not revert) and, on failure, credit the amount to a claimable mapping so the user can pull it later — preventing the push-transfer failure from blocking the global counter.

---

### Proof of Concept

1. Attacker deploys `Blocker` contract with `receive() external payable { revert(); }`.
2. `Blocker` calls `LRTWithdrawalManager.initiateWithdrawal(ETH_TOKEN, minAmount, "")` — rsETH is escrowed.
3. Operator calls `unlockQueue(ETH_TOKEN, ...)` — rsETH is burned, ETH is redeemed into `LRTWithdrawalManager`, `unlockedWithdrawalsCount[ETH]` becomes `1`.
4. Anyone calls `completeWithdrawal(ETH_TOKEN, ...)` for `Blocker` — `_transferAsset` calls `payable(Blocker).call{value: amount}("")`, `Blocker` reverts, entire tx reverts.
5. Operator calls `completeWithdrawalForUser(ETH_TOKEN, Blocker, "")` — same revert.
6. `hasUnlockedWithdrawals(ETH_TOKEN)` returns `true` permanently.
7. `sweepRemainingAssets(ETH_TOKEN)` reverts with `PendingWithdrawalsExist` forever. [8](#0-7) [9](#0-8)

### Citations

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

**File:** contracts/LRTWithdrawalManager.sol (L305-307)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
        //Take the amount to distribute from vault
        unstakingVault.redeem(asset, assetAmountUnlocked);
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

**File:** contracts/LRTWithdrawalManager.sol (L629-631)
```text
    function hasUnlockedWithdrawals(address asset) public view returns (bool hasUnlocked) {
        return unlockedWithdrawalsCount[asset] > 0;
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

**File:** contracts/LRTWithdrawalManager.sol (L877-879)
```text
        if (asset == LRTConstants.ETH_TOKEN) {
            (bool sent,) = payable(to).call{ value: amount }("");
            if (!sent) revert EthTransferFailed();
```

**File:** contracts/LRTWithdrawalManager.sol (L881-882)
```text
            IERC20(asset).safeTransfer(to, amount);
        }
```
