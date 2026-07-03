### Title
LRT Manager can block user rsETH transfers, preventing withdrawal initiation while rsETH value can still decrease - (File: contracts/RSETH.sol)

---

### Summary

`RSETH.blockUserTransfers` allows the LRT Manager to block rsETH transfers for specific users (e.g., for AML/compliance). This is a normal operational action, but it has an unintended side effect: blocked users cannot initiate or instant-withdraw their rsETH position through `LRTWithdrawalManager`, because both withdrawal paths require an rsETH transfer or burn that is gated by `_enforceNotBlocked`. Meanwhile, the rsETH exchange rate can still decrease (e.g., due to EigenLayer slashing), leaving blocked users holding depreciating rsETH with no exit path.

---

### Finding Description

`RSETH.blockUserTransfers` sets `transfersBlockedUntil[account] = block.timestamp + 1 days` for each target address. The block is refreshable indefinitely by re-calling the function before expiry. [1](#0-0) 

The internal `_enforceNotBlocked` reverts with `TransfersBlocked` if the account has an active block: [2](#0-1) 

This check is enforced in **three** places:

1. `_transfer` (called by any ERC-20 `transfer`/`transferFrom`): [3](#0-2) 

2. `burnFrom` (called by `instantWithdrawal`): [4](#0-3) 

**Withdrawal path 1 — `initiateWithdrawal`** calls `safeTransferFrom` on rsETH, which routes through `_transfer` → `_enforceNotBlocked(from)`. A blocked user's call reverts immediately: [5](#0-4) 

**Withdrawal path 2 — `instantWithdrawal`** calls `burnFrom(msg.sender, ...)`, which calls `_enforceNotBlocked(account)`. A blocked user's call also reverts: [6](#0-5) 

Neither withdrawal path checks whether the caller is blocked before attempting the rsETH movement. There is no bypass or exemption for the withdrawal manager as the `to` address, and the `from`-side block fires regardless.

The rsETH price is determined by `LRTOracle.rsETHPrice()` and can decrease at any time due to EigenLayer slashing of the underlying LST strategies. A blocked user cannot sell rsETH on secondary markets either, because `_transfer` is blocked for all destinations.

The LRT Manager can keep refreshing the block indefinitely, extending the freeze beyond 24 hours without limit.

---

### Impact Explanation

**Medium — Temporary freezing of funds.**

A user whose rsETH transfers are blocked cannot exit their position through any on-chain path (`initiateWithdrawal`, `instantWithdrawal`, or secondary-market transfer) for the duration of the block. If EigenLayer slashes the underlying assets during this window, the user suffers value loss with no ability to exit. The LRT Manager can extend the block indefinitely by refreshing it before expiry, making the freeze potentially permanent in practice.

---

### Likelihood Explanation

The LRT Manager role is expected to exercise `blockUserTransfers` for legitimate compliance or security reasons (e.g., flagging a suspicious address). The design flaw is that the protocol does not account for the fact that blocking rsETH transfers also silently blocks the withdrawal initiation path — the manager may not intend to prevent the user from withdrawing, only from transferring rsETH to third parties. This is directly analogous to the reference report: a normal operator action (disabling a market / blocking transfers) has an unintended side effect (users cannot close positions / cannot withdraw) while another mechanism continues to operate against them (liquidation / rsETH value decrease).

---

### Recommendation

Two mitigations are possible (mirroring the reference report's suggestions):

1. **Exempt the withdrawal manager from the `from`-side block check**: When the destination is `LRTWithdrawalManager`, allow the transfer even if the sender is blocked. This preserves the user's ability to exit while still preventing transfers to arbitrary third parties.

2. **Add a dedicated withdrawal-initiation path that bypasses the transfer block**: Instead of pulling rsETH via `safeTransferFrom`, allow users to call a separate function that records the withdrawal intent and locks the rsETH in-place, without triggering `_transfer`.

---

### Proof of Concept

```
1. User deposits stETH into LRTDepositPool and receives rsETH.
2. LRT Manager calls RSETH.blockUserTransfers([user]) for compliance reasons.
   → transfersBlockedUntil[user] = block.timestamp + 1 days
3. User calls LRTWithdrawalManager.initiateWithdrawal(stETH, amount, "").
   → safeTransferFrom(user, withdrawalManager, amount)
   → RSETH._transfer(user, withdrawalManager, amount)
   → _enforceNotBlocked(user)  ← reverts: TransfersBlocked(user, blockedUntil)
4. User calls LRTWithdrawalManager.instantWithdrawal(stETH, amount, "").
   → RSETH.burnFrom(user, amount)
   → _enforceNotBlocked(user)  ← reverts: TransfersBlocked(user, blockedUntil)
5. EigenLayer slashes the stETH strategy; rsETHPrice decreases.
6. LRT Manager refreshes the block before expiry → user remains frozen.
7. User's rsETH is now worth less, and they had no exit path during the slash event.
```

The root cause is in `RSETH.blockUserTransfers` (line 161) combined with the unconditional `_enforceNotBlocked(from)` in `_transfer` (line 288), with no exemption for the withdrawal manager as a trusted destination. [1](#0-0) [3](#0-2) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/RSETH.sol (L161-176)
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

**File:** contracts/RSETH.sol (L294-306)
```text
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

**File:** contracts/LRTWithdrawalManager.sol (L212-229)
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
```
