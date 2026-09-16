### Title
Front-running `SimplexPaymaster._executePermit()`'s EIP-2612 permit can grief a sponsored UserOp - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` mode `0x00` prefunds a sponsored ERC-4337 UserOp by executing an EIP-2612 `permit()` call during validation, exactly like the mETH `Staking.unstakeRequestWithPermit()` pattern in the external report. An attacker who observes the `(v, r, s)` in the mempool can front-run the permit call directly on the token, consuming the signer's nonce; the paymaster's own `permit()` call then reverts and the entire UserOp validation fails, denying the fee-payer's operation even though no funds are at risk.

### Finding Description
`_executePermit` unconditionally calls the token's `permit()` and reverts with `PermitFailed` on any failure, with no fallback to check whether the allowance was already (or otherwise) satisfied: [1](#0-0) 

This function is invoked from `_validatePaymasterUserOp` whenever `paymasterData[0] == 0x00`: [2](#0-1) 

Because the permit's `(owner, spender, value, deadline, v, r, s)` are fully visible in the pending UserOp/mempool, an attacker can extract them and call `IERC20Permit(token).permit(...)` directly before the paymaster's own call lands. The token's nonce is bumped, the pre-image signature becomes invalid for the paymaster's subsequent call, and `_executePermit`'s `try/catch` reverts the entire `_validatePaymasterUserOp`, causing bundlers to drop the UserOp — the same "signature consumed by a third party invalidates the legitimate transaction" root cause as `Staking.unstakeRequestWithPermit()` in the original report, which also does not fall back to checking the allowance before failing.

The team's own architecture notes acknowledge this exact class of griefing and explicitly declined to add an allowance fallback: [3](#0-2) 

Mode `0x00` is intentionally still reachable: it is the sole way for `DelegationService`'s first-time chain bootstrap to sponsor gas with zero standing Permit2 allowance, and it also remains generally available "on the permissionless contract for other integrators": [4](#0-3) 

### Impact Explanation
No funds are stolen — this is a griefing/denial-of-service on a single fee-sponsored operation. For the Simplex flow, the affected op is specifically the once-per-chain delegation bootstrap for a solver account (blocking that solver from onboarding on a chain until it acquires native gas or retries), and for any third-party integrator using mode `0x00` directly it can block arbitrary sponsored user operations that rely on this permit mode. This matches the Medium-severity classification of the original mETH report (targeted transaction griefing, not fund loss).

### Likelihood Explanation
High for any observer of the public mempool: the attack requires only reading a pending UserOp's calldata (permit `v, r, s` are plaintext in `paymasterData`) and submitting a plain `permit()` call with higher gas/priority before the sponsored UserOp is included — a well-known, cheap front-running technique, identical in mechanism to the original mETH finding.

### Recommendation
Wrap the `IERC20Permit.permit()` call in `_executePermit` (and analogously the `PERMIT2.permitTransferFrom` call in the mode `0x02` `_prefund` path) so a revert is tolerated when the token's allowance to the paymaster already covers `permitAmount`/`prefundAmount`, proceeding with prefund in that case instead of hard-reverting the whole validation — mirroring the recommendation given for `Staking.unstakeRequestWithPermit()`.

### Proof of Concept
1. Solver/integrator submits a UserOp whose `paymasterData` begins with mode `0x00` and contains a valid EIP-2612 permit `(owner, address(paymaster), permitAmount, deadline, v, r, s)`, per `_executePermit`: [5](#0-4) 
2. Attacker reads `(v, r, s)` from the public mempool and calls `token.permit(owner, address(paymaster), permitAmount, deadline, v, r, s)` directly (or with any lower amount/spender via a different but still-valid replay depending on the token) ahead of the bundled UserOp, consuming the owner's EIP-2612 nonce.
3. When the original UserOp is later included, `EntryPoint` calls `_validatePaymasterUserOp`, which calls `_executePermit`, which calls `permit()` again with the now-stale signature; the token reverts (invalid nonce/signature).
4. `_executePermit`'s `catch` block reverts with `PermitFailed(tokenAddr)`, causing the whole UserOp to fail validation and be dropped by the bundler, denying the sponsored operation even though the attacker gained nothing and the owner's funds are untouched.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L502-514)
```text
        bytes calldata data = userOp.paymasterData();
        if (data.length == 0) revert InvalidPaymasterData(0);
        if (uint8(data[0]) == 0x00) {
            if (data.length < 21) revert InvalidPaymasterData(data.length);
            address tokenAddr = address(bytes20(data[1:21]));
            TokenConfig memory cfg = tokenConfigs[tokenAddr];
            if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(tokenAddr);
            if (!cfg.active) revert TokenNotActive(tokenAddr);
            _executePermit(userOp);
        }

        return super._validatePaymasterUserOp(userOp, userOpHash, maxCost);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L629-649)
```text
    /// @dev Parse and execute the EIP-2612 permit from paymasterData.
    ///      Layout: mode(1) + token(20) + permitAmount(32) + deadline(32) + v(1) + r(32) + s(32) = 150 bytes
    function _executePermit(PackedUserOperation calldata userOp) internal {
        bytes calldata data = userOp.paymasterData();
        if (data.length != 150) revert InvalidPaymasterData(data.length);

        address tokenAddr = address(bytes20(data[1:21]));
        uint256 permitAmount = uint256(bytes32(data[21:53]));
        uint256 deadline = uint256(bytes32(data[53:85]));
        uint8 v = uint8(data[85]);
        bytes32 r = bytes32(data[86:118]);
        bytes32 s = bytes32(data[118:150]);

        address owner = userOp.sender;

        try IERC20Permit(tokenAddr).permit(owner, address(this), permitAmount, deadline, v, r, s) {
            emit PermitExecuted(tokenAddr, owner, permitAmount);
        } catch {
            revert PermitFailed(tokenAddr);
        }
    }
```

**File:** sdk/packages/simplex/docs/ai/decisions/2026-09-07-approve-mode-removed-on-chain-and-in-the-client.md (L13-16)
```markdown
on a chain did not share the sequential EIP-2612 nonce (every other solver already did); a
front-run permit still loses the bid, and no allowance fallback was added to `_executePermit`
because that would be APPROVE by the back door; the ERC-7562 fallback no longer exists (mode 0 was
never clean either: it reads `block.timestamp` and executes an external permit), accepted as
```

**File:** sdk/packages/simplex/docs/ai/decisions/2026-09-08-eip-2612-is-the-bootstrap-authorization-and-nothing-else.md (L3-7)
```markdown
Chosen: the `permitBootstrap` flag, set only by `DelegationService`'s first-time delegation
op, lets that one op authorize with an EIP-2612 permit when the fee token has no Permit2
allowance yet. The same op carries `approve(Permit2, max)` in its callData. Every other
sponsored op — fills, bids, vault sweeps, token sends — authorizes through Permit2 with no
way to reach the permit path.
```
