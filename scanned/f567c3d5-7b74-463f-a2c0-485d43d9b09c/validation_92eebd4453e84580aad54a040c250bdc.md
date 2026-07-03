### Title
Zero Balance Delta Revert Blocks Emergency Bridge Claim Flow - (File: contracts/bridges/SonicBridgeReceiver.sol)

### Summary
`SonicBridgeReceiver` enforces a strict `if (received == 0) revert InsufficientBalance()` guard after invoking the Sonic bridge's on-chain claim. If the Sonic bridge enters an emergency or paused state where the claim call succeeds but does not immediately transfer tokens, this guard causes a revert, blocking the primary claim-and-forward path and temporarily freezing bridged assets destined for `L1Vault`.

### Finding Description
The `SonicBridgeReceiver` contract contains a combined claim-and-transfer function that:

1. Snapshots the token balance before calling the Sonic bridge claim.
2. Calls the external Sonic bridge claim function.
3. Computes the balance delta: `uint256 received = balanceAfter - balanceBefore`.
4. **Reverts unconditionally if the delta is zero**: `if (received == 0) revert InsufficientBalance()`.
5. Forwards the received amount to `l1Vault`. [1](#0-0) 

Cross-chain bridges, including the Sonic bridge, can enter emergency or security-pause states in which the claim call does not revert but also does not immediately credit tokens to the caller — instead queuing an emergency withdrawal for later settlement by the bridge administrator. In that scenario:

- The balance delta is zero.
- The function reverts at line 94 with `InsufficientBalance`.
- The primary claim-and-forward path is permanently blocked for that withdrawal ID until the emergency is resolved.

Furthermore, during the emergency recovery flow the Sonic bridge administrator may push tokens directly to `SonicBridgeReceiver` (a path that never occurs in normal operation). The contract does expose a `CLAIMER_ROLE`-gated `transferToVault` escape hatch and a separate `claimWithdrawal` function, but neither is documented as the emergency recovery path, and the primary path's revert prevents automatic forwarding. [2](#0-1) [3](#0-2) 

### Impact Explanation
**Medium — Temporary freezing of funds.**

When the Sonic bridge enters an emergency state, every call to the primary claim-and-transfer function reverts. Bridged assets cannot reach `L1Vault` through the normal path. The `LRTWithdrawalManager` and `LRTUnstakingVault` downstream are starved of liquidity, blocking pending user withdrawals until a `CLAIMER_ROLE` operator manually discovers the emergency, calls `claimWithdrawal`, waits for the bridge administrator to push tokens, and then calls `transferToVault`. The window of freezing is bounded only by operator response time and bridge recovery time.

### Likelihood Explanation
**Low-to-Medium.** The Sonic bridge is a live cross-chain bridge with a known emergency/pause mechanism. Bridge emergency states are a realistic operational scenario (security incidents, governance actions, liquidity crises). The trigger requires no attacker action — it is a normal bridge-side event that the `SonicBridgeReceiver` is not designed to handle gracefully.

### Recommendation
1. **Treat zero delta as a no-op success** in the combined claim-and-transfer function. If `received == 0`, emit an event and return without reverting, preserving the ability to retry or use the manual path.
2. **Document and test the emergency recovery path** (`claimWithdrawal` → bridge admin pushes tokens → `transferToVault`) so operators can act quickly when the primary path is blocked.
3. Consider adding a `rescueTokens` function callable by `DEFAULT_ADMIN_ROLE` to recover any ERC-20 tokens that arrive at `SonicBridgeReceiver` outside the normal flow.

### Proof of Concept
1. User bridges rsETH/LST from Sonic chain; a withdrawal ID is registered on the Sonic bridge.
2. The Sonic bridge enters an emergency state (e.g., security pause). The on-chain claim function no longer transfers tokens immediately — it queues an emergency withdrawal instead.
3. The `CLAIMER_ROLE` operator calls the primary claim-and-transfer function in `SonicBridgeReceiver`.
4. Internally, `ETHEREUM_TOKEN_DEPOSIT.claim(withdrawalId, token, amount, proof)` is called and returns without reverting, but transfers zero tokens.
5. `balanceAfter - balanceBefore == 0` → `revert InsufficientBalance()` fires at line 94.
6. The withdrawal ID is not marked as claimed (state is rolled back), so the operator cannot proceed with `claimWithdrawal` without understanding the emergency state.
7. Bridged assets are frozen in the Sonic bridge's emergency queue; `L1Vault` receives no liquidity; downstream user withdrawals stall. [1](#0-0)

### Citations

**File:** contracts/bridges/SonicBridgeReceiver.sol (L91-98)
```text
        // Verify we received the tokens and transfer to L1Vault
        uint256 balanceAfter = IERC20(token).balanceOf(address(this));
        uint256 received = balanceAfter - balanceBefore;
        if (received == 0) revert InsufficientBalance();

        // Transfer tokens to L1Vault
        IERC20(token).safeTransfer(l1Vault, received);
        emit TokensTransferredToVault(token, received, l1Vault);
```

**File:** contracts/bridges/SonicBridgeReceiver.sol (L106-123)
```text
    function claimWithdrawal(
        uint256 withdrawalId,
        address token,
        uint256 amount,
        bytes calldata proof
    )
        external
        nonReentrant
        onlyRole(CLAIMER_ROLE)
    {
        if (withdrawalId == 0) revert InvalidWithdrawalId();
        if (claimedWithdrawals[withdrawalId]) revert WithdrawalAlreadyClaimed();

        claimedWithdrawals[withdrawalId] = true;

        ETHEREUM_TOKEN_DEPOSIT.claim(withdrawalId, token, amount, proof);
        emit WithdrawalClaimed(withdrawalId, token, amount);
    }
```

**File:** contracts/bridges/SonicBridgeReceiver.sol (L125-135)
```text
    /// @notice Manually transfer tokens to L1Vault (for claimed but not transferred tokens)
    /// @param token The token address to transfer
    /// @param amount The amount to transfer (0 = transfer all)
    function transferToVault(address token, uint256 amount) external nonReentrant onlyRole(CLAIMER_ROLE) {
        uint256 balance = IERC20(token).balanceOf(address(this));
        uint256 transferAmount = amount == 0 ? balance : amount;
        if (transferAmount > balance) revert InsufficientBalance();

        IERC20(token).safeTransfer(l1Vault, transferAmount);
        emit TokensTransferredToVault(token, transferAmount, l1Vault);
    }
```
