### Title
Blocked User Can Bypass rsETH Transfer Restriction by Completing a Pre-Initiated Withdrawal — (File: contracts/LRTWithdrawalManager.sol)

### Summary
`RSETH.sol` implements a 24-hour transfer-block mechanism (`transfersBlockedUntil`) intended to freeze a flagged user's rsETH. However, `LRTWithdrawalManager.completeWithdrawal` never checks whether the withdrawing user is blocked before disbursing ETH/LST. A user who queued a withdrawal before being blocked can still exit the protocol and receive underlying assets, defeating the freeze entirely.

---

### Finding Description

`RSETH._enforceNotBlocked` is called in three places:

- `mint` — checks the recipient before minting [1](#0-0) 
- `burnFrom` — checks the account before burning [2](#0-1) 
- `_transfer` — checks both `from` and `to` before any ERC-20 transfer [3](#0-2) 

When a user calls `initiateWithdrawal`, rsETH is transferred **from the user to `LRTWithdrawalManager`**:

```solidity
IERC20(lrtConfig.rsETH()).safeTransferFrom(msg.sender, address(this), rsETHUnstaked);
``` [4](#0-3) 

This `safeTransferFrom` triggers `RSETH._transfer`, which calls `_enforceNotBlocked(msg.sender)`. So a **currently blocked** user cannot initiate a new withdrawal. However, if the user initiated the withdrawal **before** being blocked, the rsETH is already held by `LRTWithdrawalManager`.

Later, `completeWithdrawal` calls `_processWithdrawalCompletion`, which unconditionally transfers ETH or LST to the user:

```solidity
_transferAsset(asset, user, request.expectedAssetAmount);
``` [5](#0-4) 

`_transferAsset` sends native ETH via `call` or LST via `safeTransfer` — **neither path touches `RSETH._enforceNotBlocked`**:

```solidity
function _transferAsset(address asset, address to, uint256 amount) internal {
    if (asset == LRTConstants.ETH_TOKEN) {
        (bool sent,) = payable(to).call{ value: amount }("");
        if (!sent) revert EthTransferFailed();
    } else {
        IERC20(asset).safeTransfer(to, amount);
    }
}
``` [6](#0-5) 

The rsETH was already burned by the operator during `unlockQueue`:

```solidity
if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
``` [7](#0-6) 

So by the time `completeWithdrawal` is called, the rsETH no longer exists in the user's wallet — the admin's `recoverFrozenFunds` can only recover rsETH held **at the blocked address**:

```solidity
uint256 accountBalance = balanceOf(from);
super._transfer(from, custodyAddress, accountBalance);
``` [8](#0-7) 

Since the rsETH was moved to `LRTWithdrawalManager` before the block was applied, `recoverFrozenFunds` finds zero balance at the user's address and cannot intercept the exit.

---

### Impact Explanation

The blocking mechanism's purpose is to freeze a flagged user's economic position in the protocol. A user who queued a withdrawal before being blocked can still receive ETH or LST through `completeWithdrawal`, fully exiting the protocol. The admin has no on-chain mechanism to stop this once the withdrawal is in the queue and the rsETH has been burned by `unlockQueue`. This constitutes a **temporary (and in practice permanent for that position) freezing bypass** — the user's funds cannot be frozen or recovered.

**Impact: Medium** — Temporary freezing of funds (the blocked user exits with their underlying assets).

---

### Likelihood Explanation

The standard `withdrawalDelayBlocks` is set to `8 days / 12 seconds` (~57,600 blocks):

```solidity
withdrawalDelayBlocks = 8 days / 12 seconds;
``` [9](#0-8) 

This 8-day window between `initiateWithdrawal` and `completeWithdrawal` is a realistic gap during which a compliance event could trigger a block. Any user who is flagged after initiating a withdrawal — but before completing it — can exploit this gap. No special permissions or front-running are required; the user simply waits for the delay to pass and calls `completeWithdrawal`.

**Likelihood: Medium.**

---

### Recommendation

Add a blocked-user check inside `_processWithdrawalCompletion` before disbursing assets:

```solidity
// In _processWithdrawalCompletion, before _transferAsset:
IRSETH rseth = IRSETH(lrtConfig.rsETH());
if (rseth.transfersBlockedUntil(user) != 0 &&
    block.timestamp < rseth.transfersBlockedUntil(user) &&
    !rseth.isPermanentlyExempt(user)) {
    revert UserTransfersBlocked(user);
}
```

Alternatively, expose a view function on `RSETH` (e.g., `isBlocked(address)`) and call it in `_processWithdrawalCompletion`. This mirrors the pattern already used in `mint` and `burnFrom`.

---

### Proof of Concept

1. Alice holds rsETH and calls `LRTWithdrawalManager.initiateWithdrawal(ETH, amount, "")`. Her rsETH is transferred to `LRTWithdrawalManager`. [10](#0-9) 
2. Admin detects suspicious activity and calls `RSETH.blockUserTransfers([Alice])`, setting `transfersBlockedUntil[Alice] = block.timestamp + 1 days`. [11](#0-10) 
3. Admin calls `RSETH.recoverFrozenFunds(Alice)` — Alice's rsETH balance is 0 (already in `LRTWithdrawalManager`), so nothing is recovered. [12](#0-11) 
4. Operator calls `unlockQueue` — Alice's rsETH is burned from `LRTWithdrawalManager`. [7](#0-6) 
5. After 8 days, Alice calls `completeWithdrawal(ETH, "")`. `_processWithdrawalCompletion` performs no block check and sends ETH to Alice. [13](#0-12) 
6. Alice has exited the protocol with her underlying ETH despite being blocked.

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

**File:** contracts/RSETH.sol (L238-239)
```text
        _enforceNotBlocked(to);
        _mint(to, amount);
```

**File:** contracts/RSETH.sol (L245-247)
```text
    function burnFrom(address account, uint256 amount) external onlyRole(LRTConstants.BURNER_ROLE) whenNotPaused {
        _enforceNotBlocked(account);
        _burn(account, amount);
```

**File:** contracts/RSETH.sol (L287-291)
```text
    function _transfer(address from, address to, uint256 amount) internal override {
        _enforceNotBlocked(from);
        _enforceNotBlocked(to);
        super._transfer(from, to, amount);
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

**File:** contracts/LRTWithdrawalManager.sol (L305-305)
```text
        if (rsETHBurned != 0) IRSETH(lrtConfig.rsETH()).burnFrom(address(this), rsETHBurned);
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
