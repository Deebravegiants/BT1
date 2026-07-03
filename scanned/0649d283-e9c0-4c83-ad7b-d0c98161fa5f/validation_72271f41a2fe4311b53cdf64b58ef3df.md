### Title
Blocked rsETH Holders Can Complete Pending Withdrawal Requests, Bypassing the Transfer Restriction Mechanism - (File: contracts/LRTWithdrawalManager.sol)

---

### Summary

`RSETH.sol` implements a transfer-blocking mechanism (`transfersBlockedUntil`) that prevents blocked accounts from sending or receiving rsETH. However, `LRTWithdrawalManager.completeWithdrawal()` sends ETH/LST assets to the user without checking whether the user is currently blocked. A user who initiated a withdrawal before being blocked can complete it and receive underlying assets during the active block window, defeating the regulatory freeze intent.

---

### Finding Description

`RSETH._transfer` enforces `_enforceNotBlocked` on both `from` and `to`: [1](#0-0) 

`burnFrom` also enforces the block: [2](#0-1) 

The async withdrawal lifecycle is:

1. **`initiateWithdrawal`** — transfers rsETH from the user to the withdrawal manager via `safeTransferFrom`. Because `_transfer` checks `_enforceNotBlocked(from)`, a currently-blocked user cannot initiate a new withdrawal. [3](#0-2) 

2. **`unlockQueue`** (operator) — burns rsETH held by the withdrawal manager and marks requests as unlocked.

3. **`completeWithdrawal`** — sends ETH/LST to `msg.sender`. This step involves **no rsETH transfer** and performs **no block check** on the recipient: [4](#0-3) 

Because the rsETH was already moved to the withdrawal manager during step 1, the admin's `recoverFrozenFunds` cannot recover it from the user's address (the user's rsETH balance is zero). The admin has no mechanism to intercept or cancel the pending withdrawal request. The user can call `completeWithdrawal` at any time — including while their address is actively blocked — and receive ETH/LST.

The `blockUserTransfers` function is documented as a 24-hour freeze that can be refreshed indefinitely: [5](#0-4) 

Yet this freeze has no effect on the completion leg of an already-queued withdrawal.

---

### Impact Explanation

**Medium — Temporary freezing bypass.**

A user who is blocked for regulatory reasons (e.g., OFAC compliance, suspicious activity) and who has a pending withdrawal request can call `completeWithdrawal` during the active block window and receive ETH or LST assets. The admin cannot prevent this: `recoverFrozenFunds` only operates on the user's own rsETH balance, which is zero once the withdrawal was initiated. The protocol's stated ability to freeze and recover funds from blocked accounts is therefore incomplete for funds already in the withdrawal queue.

---

### Likelihood Explanation

**Medium.** The scenario requires the user to have initiated a withdrawal before being blocked. Given that the withdrawal delay is 8 days (`withdrawalDelayBlocks = 8 days / 12 seconds`) and the block is 24 hours (refreshable), there is a realistic window where a user is blocked after initiating a withdrawal but before completing it. A sophisticated user aware of impending regulatory action could front-run the block by initiating a withdrawal first. [6](#0-5) 

---

### Recommendation

Add a block check in `_processWithdrawalCompletion` (or in `completeWithdrawal` directly) against the recipient address before transferring ETH/LST:

```solidity
// In _processWithdrawalCompletion, before transferring assets to user:
IRSETH(lrtConfig.rsETH()).enforceNotBlocked(user); // expose _enforceNotBlocked as external/internal
```

Alternatively, expose `_enforceNotBlocked` as an internal view on `RSETH` and call it from the withdrawal manager, or add a dedicated `isBlocked(address)` view function to `RSETH` that the withdrawal manager can query before releasing assets.

Additionally, consider adding a mechanism for the admin to cancel or redirect pending withdrawal requests for blocked users, analogous to how `recoverFrozenFunds` handles rsETH balances held directly by users.

---

### Proof of Concept

1. Alice calls `initiateWithdrawal(stETH, 1e18, "")` — 1 rsETH is transferred to `LRTWithdrawalManager`. Alice's rsETH balance is now 0.
2. Admin calls `RSETH.blockUserTransfers([Alice])` — Alice is blocked until `block.timestamp + 1 days`.
3. Admin calls `RSETH.recoverFrozenFunds(Alice)` — **reverts** because Alice's rsETH balance is 0; the rsETH is held by the withdrawal manager.
4. Operator calls `unlockQueue(stETH, ...)` — Alice's request is unlocked, rsETH is burned from the withdrawal manager.
5. Alice calls `completeWithdrawal(stETH, "")` — **succeeds**. Alice receives stETH despite being actively blocked. [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/RSETH.sol (L156-177)
```text
    /// @notice Block transfers TO and FROM given users for 24 hours
    /// @dev Re-applying the block before expiry refreshes the hold to `block.timestamp + 1 days`
    ///      (i.e. not cumulative; never more than 24h from the latest call). Exempt addresses cannot be blocked.
    ///      Emits {UserTransfersBlocked} only when the timestamp changes.
    /// @param accounts Addresses to block.
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

**File:** contracts/RSETH.sol (L245-248)
```text
    function burnFrom(address account, uint256 amount) external onlyRole(LRTConstants.BURNER_ROLE) whenNotPaused {
        _enforceNotBlocked(account);
        _burn(account, amount);
    }
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

**File:** contracts/LRTWithdrawalManager.sol (L183-185)
```text
    function completeWithdrawal(address asset, string calldata referralId) external nonReentrant whenNotPaused {
        _processWithdrawalCompletion(asset, msg.sender, referralId);
    }
```
