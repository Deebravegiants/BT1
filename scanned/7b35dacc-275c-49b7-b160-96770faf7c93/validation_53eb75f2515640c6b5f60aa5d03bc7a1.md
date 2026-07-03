### Title
Pause Duration Exceeding 24-Hour Transfer Block Allows Blocked rsETH Holders to Escape Fund Recovery - (File: contracts/RSETH.sol)

### Summary
`RSETH.sol` implements a 24-hour transfer-block mechanism (`blockUserTransfers`) paired with a fund-seizure function (`recoverFrozenFunds`). Because `unpause()` is restricted to `onlyLRTAdmin` (a timelock/multisig that may require > 24 hours to act), and because `_transfer` is **not** guarded by `whenNotPaused`, a blocked user can wait for their 24-hour block to expire during a pause and then freely transfer their rsETH away — permanently defeating the recovery mechanism.

### Finding Description

`blockUserTransfers` sets a 24-hour transfer block: [1](#0-0) 

`recoverFrozenFunds` enforces that the block must still be active: [2](#0-1) 

`pause()` is callable by the fast-acting `PAUSER_ROLE`, but `unpause()` requires `onlyLRTAdmin` — the `DEFAULT_ADMIN_ROLE`, which maps to a timelock/multisig that may impose a delay exceeding 24 hours: [3](#0-2) 

Critically, the `_transfer` override does **not** include `whenNotPaused`: [4](#0-3) 

`_enforceNotBlocked` auto-cleans expired blocks, meaning once `block.timestamp >= blockedUntil`, the mapping entry is deleted and the user is free to transfer: [5](#0-4) 

The `onlyLRTAdmin` modifier resolves to `DEFAULT_ADMIN_ROLE` in `LRTConfigRoleChecker`: [6](#0-5) 

### Impact Explanation

When a pause lasts longer than 24 hours:

1. The blocked user's `transfersBlockedUntil` timestamp expires.
2. Because `_transfer` has no `whenNotPaused` guard, the user can call `RSETH.transfer(newAddress, balance)` **while the contract is still paused**. `_enforceNotBlocked` auto-cleans the expired entry and allows the transfer.
3. `recoverFrozenFunds` subsequently reverts with `NoActiveTransferBlock` because `transfersBlockedUntil[from]` is now `0`.
4. The funds have moved to an unblocked address; the recovery window is permanently lost.

**Impact: Low** — the contract fails to deliver its promised fund-recovery guarantee without any direct loss of protocol-owned value, but the seizure mechanism is rendered permanently ineffective for the affected user.

### Likelihood Explanation

The `PAUSER_ROLE` (security council) can pause instantly. `unpause()` requires `onlyLRTAdmin`, which in a standard governance setup is a timelock with a minimum delay that can easily exceed 24 hours. Any pause triggered for an unrelated incident (e.g., a deposit-pool bug) while a user is under a transfer block creates this window. No attacker action is required beyond waiting.

### Recommendation

1. Add `whenNotPaused` to `_transfer` in `RSETH.sol` so that rsETH transfers are also blocked during a pause, preventing the blocked user from moving funds while the contract is paused.
2. Alternatively, store an `unpauseTime` and require `recoverFrozenFunds` to check `max(blockedUntil, unpauseTime)` so the recovery window is extended by the duration of any pause that overlapped with the block.
3. Consider granting `unpause()` to a faster-acting role (e.g., the same `PAUSER_ROLE` or a dedicated unpauser) so the pause duration is bounded well below 24 hours.

### Proof of Concept

```
T=0:    Manager calls blockUserTransfers([alice])
        → transfersBlockedUntil[alice] = T + 1 days

T=1h:   Security council calls pause() (unrelated incident)
        → RSETH is paused; unpause requires onlyLRTAdmin (timelock, 48h delay)

T=25h:  alice's block has expired (T + 1 days = T + 24h < T + 25h)
        alice calls RSETH.transfer(bob, aliceBalance)
        → _transfer() has no whenNotPaused guard
        → _enforceNotBlocked(alice): block.timestamp >= blockedUntil → deletes entry → passes
        → transfer succeeds; alice's rsETH is now at bob

T=49h:  Admin finally unpause()s
        Admin calls recoverFrozenFunds(alice)
        → transfersBlockedUntil[alice] == 0 → revert NoActiveTransferBlock
        Recovery is permanently impossible for alice's original balance.
```

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

**File:** contracts/RSETH.sol (L184-191)
```text
    function pause() external onlyRole(LRTConstants.PAUSER_ROLE) {
        _pause();
    }

    /// @dev Returns to normal state. Contract must be paused.
    function unpause() external onlyLRTAdmin {
        _unpause();
    }
```

**File:** contracts/RSETH.sol (L206-213)
```text
    function recoverFrozenFunds(address from) external onlyLRTAdmin {
        UtilLib.checkNonZeroAddress(from);
        UtilLib.checkNonZeroAddress(custodyAddress);

        if (isPermanentlyExempt[from]) revert AddressPermanentlyExempt(from);

        uint256 blockedUntil = transfersBlockedUntil[from];
        if (blockedUntil == 0 || block.timestamp >= blockedUntil) revert NoActiveTransferBlock(from);
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

**File:** contracts/utils/LRTConfigRoleChecker.sol (L58-63)
```text
    modifier onlyLRTAdmin() {
        if (!IAccessControl(address(lrtConfig)).hasRole(LRTConstants.DEFAULT_ADMIN_ROLE, msg.sender)) {
            revert ILRTConfig.CallerNotLRTConfigAdmin();
        }
        _;
    }
```
