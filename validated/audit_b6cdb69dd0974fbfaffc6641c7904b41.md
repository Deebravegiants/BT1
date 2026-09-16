### Title
Front-running `SimplexPaymaster._executePermit` griefs EIP-2612 PERMIT mode UserOps, blocking a solver's zero-native delegation bootstrap - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` mode `0x00` (PERMIT) executes an EIP-2612 permit inside `_validatePaymasterUserOp` before prefunding gas. Because `_executePermit` immediately reverts the entire validation on any permit failure instead of checking whether the resulting allowance is already sufficient, an attacker can front-run the sponsored UserOp by submitting the same signed permit directly to the token contract, causing the paymaster's own `permit` call to revert with `PermitFailed` and the whole UserOp to fail — even though the allowance the permit was meant to establish already exists.

### Finding Description
`_validatePaymasterUserOp` calls `_executePermit(userOp)` for mode `0x00` paymasterData before delegating to the base prefund logic: [1](#0-0) 

`_executePermit` parses the EIP-2612 `(owner, spender=paymaster, permitAmount, deadline, v, r, s)` fields straight out of `userOp.paymasterData()` and calls `IERC20Permit(tokenAddr).permit(...)` in a `try/catch` that reverts with `PermitFailed(tokenAddr)` on any failure — with no fallback check of the resulting allowance: [2](#0-1) 

This is the identical root cause as the external report on `Permit2Proxy.callDiamondWithEIP2612Signature`: the signature (`owner`, `spender`, `amount`, `deadline`, `v`, `r`, `s`) is fully contained in public data (here, the UserOperation broadcast to the bundler/mempool, or observable through the pending op before inclusion). An attacker copies these values and calls `token.permit(owner, paymaster, permitAmount, deadline, v, r, s)` directly, consuming the EIP-2612 sequential nonce for `owner`. When the solver's original UserOp is later included, `_executePermit`'s `permit` call reverts (`EIP2612: invalid signature`/nonce mismatch), and `SimplexPaymaster` unconditionally reverts with `PermitFailed`, failing the entire UserOp validation — even though the attacker's front-run call already installed the exact allowance the permit was signed for.

Design docs confirm mode `0x00` is reachable only through the `permitBootstrap` path, exercised by exactly one privileged-in-purpose but unprivileged-in-execution operation: the solver's first-time delegation on a chain, used specifically because the solver holds zero native token and cannot fund a direct `approve`: [3](#0-2) 

Because this is the *only* zero-native path for a solver to install the Permit2 allowance needed to operate on a new chain, an attacker can specifically target it to prevent a targeted solver from ever bootstrapping without funding native gas — directly frustrating the documented design goal of "no native tx" onboarding.

### Impact Explanation
Any unprivileged intent solver using `SimplexPaymaster`'s mode `0x00` PERMIT bootstrap is exposed: an attacker monitoring the public bundler mempool (or the UserOp broadcast) extracts the EIP-2612 signature fields and submits a plain transaction calling `permit` on the token directly, ahead of the solver's UserOp. The solver's sponsored UserOp then unconditionally reverts in `_validatePaymasterUserOp`/`_executePermit`, even though the allowance now exists. Because the whole purpose of this path is to let a solver with zero native token bootstrap delegation and Permit2 approval on a new chain, repeated griefing can indefinitely deny that solver's ability to onboard onto the chain without funding native gas — a denial-of-service against the solver's participation route (unable to deliver fills/bids on that chain) rather than direct fund loss. This matches the "route unable to deliver messages" impact class for an unprivileged intent-solver-reachable path.

### Likelihood Explanation
High likelihood of feasibility: the attack requires only observing a pending, publicly broadcast UserOperation (ERC-4337 ops using mode `0x00` paymasterData are visible pre-inclusion via the bundler mempool) and submitting an ordinary front-running transaction with higher gas — no special privilege, funds at risk, or protocol access is needed. The only cost to the attacker is gas for the `permit` call. Given the permit bootstrap is described as happening once per chain per solver, a persistent attacker can repeatedly target new bootstrap attempts.

### Recommendation
Wrap the `permit` call in `_executePermit` (evm/src/utils/SimplexPaymaster.sol) in a `try/catch` that, on failure, checks the token's current allowance from `owner` to the paymaster (`IERC20(tokenAddr).allowance(owner, address(this))`) and proceeds if it already covers `permitAmount` (or the amount actually required for prefunding), instead of unconditionally reverting with `PermitFailed`. This mirrors the LI.FI fix (commit `bdf16c01`) referenced in the external report.

### Proof of Concept
1. Solver builds and signs a mode `0x00` UserOp for `SimplexPaymaster` per `buildPermitMode`, embedding `(owner=solverAccount, spender=paymaster, permitAmount, deadline, v, r, s)` in `paymasterData` [4](#0-3) .
2. Solver submits this UserOp to a bundler; it sits in the public UserOp mempool before inclusion.
3. Attacker extracts `(owner, permitAmount, deadline, v, r, s)` from the pending calldata and calls `IERC20Permit(token).permit(owner, paymaster, permitAmount, deadline, v, r, s)` directly with higher gas, landing first and consuming the token's EIP-2612 nonce for `owner`.
4. Solver's UserOp is included; `_validatePaymasterUserOp` → `_executePermit` calls `permit(...)` again with the now-stale signature; the ERC20 permit reverts with an invalid-signature/nonce error.
5. `_executePermit`'s catch block reverts with `PermitFailed(tokenAddr)`, unconditionally failing the entire `_validatePaymasterUserOp`, even though step 3 already installed the exact allowance the permit intended to grant [5](#0-4) .

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L502-511)
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

**File:** sdk/packages/simplex/docs/ai/decisions/2026-09-08-eip-2612-is-the-bootstrap-authorization-and-nothing-else.md (L1-24)
```markdown
# 2026-09-08 — EIP-2612 is the bootstrap authorization, and nothing else

Chosen: the `permitBootstrap` flag, set only by `DelegationService`'s first-time delegation
op, lets that one op authorize with an EIP-2612 permit when the fee token has no Permit2
allowance yet. The same op carries `approve(Permit2, max)` in its callData. Every other
sponsored op — fills, bids, vault sweeps, token sends — authorizes through Permit2 with no
way to reach the permit path.

Alternatives considered: dropping 2612 outright (the previous entry) and accepting that a
fresh solver needs native dust per chain; or restoring 2612 as the general preference for
permit-capable tokens, as it was before.

Why the scoping is the whole design. The objection to 2612 is its nonce: one sequential
counter per owner, so two permits signed for the same solver carry the same value and only
one lands. That is fatal for fills, which are the ops that actually run concurrently. It is
free for the delegation, which happens once per chain and provably has no concurrent
sibling — the account is not even delegated yet. Confining the permit to that op keeps the
serialization hazard away from everything that could hit it.

Dropping it outright lost more than it looked. The permit is the only authorization that
needs no prior on-chain state, so it is the only way an account with stablecoins and zero
native can pay for anything. Requiring native dust per chain sounds minor until it is the
operator's first run on a new chain and the failure is "send ETH here" rather than "it
worked".
```

**File:** sdk/packages/simplex/src/services/paymaster/provider/simplex.ts (L354-388)
```typescript
async function buildPermitMode(
	client: PublicClient,
	signer: Pick<Signer, "signTypedData">,
	solverAccount: HexString,
	paymasterAddress: HexString,
	tokenAddress: HexString,
	permitAmount: bigint,
	chainId: number,
): Promise<PaymasterResult> {
	const permitSignature = await signEip2612Permit(
		client,
		signer,
		solverAccount,
		paymasterAddress,
		tokenAddress,
		permitAmount,
		chainId,
	)

	const r = `0x${permitSignature.slice(2, 66)}` as HexString
	const s = `0x${permitSignature.slice(66, 130)}` as HexString
	const v = Number.parseInt(permitSignature.slice(130, 132), 16)

	const paymasterData = encodePacked(
		["uint8", "address", "uint256", "uint256", "uint8", "bytes32", "bytes32"],
		[0, tokenAddress, permitAmount, maxUint256, v, r, s],
	) as HexString

	return {
		paymaster: paymasterAddress,
		paymasterData,
		paymasterVerificationGasLimit: VERIFICATION_GAS_LIMIT_PERMIT,
		paymasterPostOpGasLimit: POST_OP_GAS_LIMIT_SIMPLEX,
	}
}
```
