All six code claims check out against the actual source. Let me verify the key facts:

- `_transfer` at L287-291 has **no** `whenNotPaused` guard [1](#0-0) 
- `_enforceNotBlocked` auto-deletes expired blocks at L304-305 [2](#0-1) 
- `recoverFrozenFunds` reverts if `block.timestamp >= blockedUntil` at L213 [3](#0-2) 
- `pause()` uses `PAUSER_ROLE`; `unpause()` uses `onlyLRTAdmin` (DEFAULT_ADMIN_ROLE) at L184-191 [4](#0-3) 
- `onlyLRTAdmin` maps to `DEFAULT_ADMIN_ROLE` at L58-63 [5](#0-4) 

The exploit path is real: a blocked rsETH holder (unprivileged) can call the public `transfer()` function while the contract is paused, because `_transfer` lacks `whenNotPaused`. Once the 24-hour block expires during a pause, `_enforceNotBlocked` auto-cleans the entry and the transfer succeeds, permanently defeating `recoverFrozenFunds`. The impact maps to **Low — contract fails to deliver promised returns**.

---

Audit Report

## Title
Missing `whenNotPaused` in `_transfer` Allows Blocked Users to Escape Fund Recovery During Extended Pause - (File: contracts/RSETH.sol)

## Summary
`RSETH._transfer` lacks a `whenNotPaused` guard, so rsETH transfers remain executable even when the contract is paused. Because `unpause()` is restricted to `onlyLRTAdmin` (a role that may be assigned to a timelock with a delay exceeding 24 hours), a user whose transfers were blocked via `blockUserTransfers` can wait for their 24-hour block to expire during a pause and then freely transfer their rsETH away. This permanently defeats `recoverFrozenFunds`, which requires an active block to execute.

## Finding Description
`blockUserTransfers` sets `transfersBlockedUntil[account] = block.timestamp + 1 days`. `recoverFrozenFunds` enforces `if (blockedUntil == 0 || block.timestamp >= blockedUntil) revert NoActiveTransferBlock(from)`, meaning recovery is only possible while the block is active. `pause()` is callable by the fast-acting `PAUSER_ROLE`, but `unpause()` requires `onlyLRTAdmin`, which resolves to `DEFAULT_ADMIN_ROLE` in `LRTConfigRoleChecker` — a role typically assigned to a timelock or multisig that may impose a delay well above 24 hours. The critical gap is that `_transfer` only calls `_enforceNotBlocked` and then `super._transfer`; it has no `whenNotPaused` check. `_enforceNotBlocked` auto-deletes the mapping entry once `block.timestamp >= blockedUntil`, so after the 24-hour window expires the blocked user can call `transfer()` successfully even while the contract is paused. After the transfer, `transfersBlockedUntil[from]` is `0`, and any subsequent call to `recoverFrozenFunds` reverts with `NoActiveTransferBlock`.

## Impact Explanation
The `recoverFrozenFunds` mechanism is permanently defeated for the affected user: the protocol cannot seize the rsETH it intended to recover. No protocol-owned value is directly lost, but the contract fails to deliver its stated fund-recovery guarantee. This matches the allowed impact: **Low — contract fails to deliver promised returns, but doesn't lose value**.

## Likelihood Explanation
No attacker capability beyond holding rsETH is required. The preconditions — being placed under a transfer block and the contract being paused for an unrelated reason — are both normal operational events that can occur independently. Any pause triggered by the `PAUSER_ROLE` (e.g., for a deposit-pool bug) while a user is under a transfer block creates this window. The blocked user need only wait passively for 24 hours and then call `transfer()`. No collusion, front-running, or special knowledge is needed.

## Recommendation
1. Add `whenNotPaused` to `_transfer` in `RSETH.sol` so that all rsETH transfers are blocked during a pause, preventing a blocked user from moving funds while the contract is paused.
2. Alternatively, extend the recovery window: store the pause start time and require `recoverFrozenFunds` to check `max(blockedUntil, unpauseTime)` so the recovery deadline is extended by the duration of any overlapping pause.
3. Consider granting `unpause()` to a faster-acting role (e.g., the same `PAUSER_ROLE` or a dedicated unpauser) to bound the maximum pause duration well below 24 hours.

## Proof of Concept
```
T=0:    onlyLRTManager calls blockUserTransfers([alice])
        → transfersBlockedUntil[alice] = T + 1 days

T=1h:   PAUSER_ROLE calls pause()
        → RSETH is paused; unpause requires onlyLRTAdmin (timelock, 48h delay)

T=25h:  alice's block has expired (T + 24h < T + 25h)
        alice calls RSETH.transfer(bob, aliceBalance)
        → _transfer(): no whenNotPaused guard → proceeds
        → _enforceNotBlocked(alice): block.timestamp >= blockedUntil
          → deletes transfersBlockedUntil[alice] → passes
        → super._transfer() succeeds; alice's rsETH is now at bob

T=49h:  Admin unpause()s
        Admin calls recoverFrozenFunds(alice)
        → transfersBlockedUntil[alice] == 0
        → revert NoActiveTransferBlock(alice)
        Recovery is permanently impossible.
```

Foundry test sketch:
```solidity
function test_blockedUserEscapesDuringPause() public {
    // Setup: block alice, then pause
    vm.prank(manager);
    rsETH.blockUserTransfers(toArray(alice));
    vm.prank(pauser);
    rsETH.pause();

    // Warp past the 24-hour block
    vm.warp(block.timestamp + 25 hours);

    // Alice transfers while paused — should succeed (demonstrates the bug)
    vm.prank(alice);
    rsETH.transfer(bob, rsETH.balanceOf(alice));

    // Admin tries to recover — reverts
    vm.prank(admin);
    vm.expectRevert(abi.encodeWithSelector(RSETH.NoActiveTransferBlock.selector, alice));
    rsETH.recoverFrozenFunds(alice);
}
```

### Citations

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

**File:** contracts/RSETH.sol (L212-213)
```text
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

**File:** contracts/RSETH.sol (L302-305)
```text
        if (block.timestamp < blockedUntil) revert TransfersBlocked(account, blockedUntil);

        // Auto-clean up expired block
        delete transfersBlockedUntil[account];
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
