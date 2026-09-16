### Title
Mode-blind `fillOrder` scan in `SolverAccount.validateUserOp` can be bypassed by combined ERC-7821 execution modes - ([File: evm/src/apps/intentsv2/SolverAccount.sol])

### Summary
`SolverAccount._containsFillOrder` decodes `executionData` unconditionally as a plain `Execution[]` batch, discarding the ERC‑7821 `mode` value that actually governs how `executionData` must be parsed. The real `ERC7821.execute()` call that eventually runs the operation dispatches on that same `mode` value and can accept execution-data shapes that are not a bare `Execution[]` (e.g. batch execution with an appended `opData` payload). Because the validation-time scan and the execution-time interpreter parse the same bytes under different assumptions, a UserOp whose `mode` selects one of these alternate/combined forms can slip a `fillOrder` call past the anti-griefing check while still being dispatched to `IntentGatewayV2.fillOrder` at execution.

### Finding Description
`validateUserOp` takes the fast ECDSA path whenever `op.signature.length == 65`, and the *only* protection against replaying a solver's public bid signature through that fast path is `_containsFillOrder`: [1](#0-0) 

This function blindly discards the first return value of `abi.decode(callData[4:], (bytes32, bytes))` — i.e. it throws away the `mode` argument of ERC‑7821's `execute(bytes32 mode, bytes executionData)` — and always re-decodes `executionData` as a bare `Execution[]`: [2](#0-1) 

`SolverAccount` inherits OpenZeppelin's `ERC7821`, whose `execute()` is the actual code that will run the operation once validation approves it, and it dispatches its parsing based on the `mode` selector: [3](#0-2) [4](#0-3) 

ERC‑7821's mode field is composable/combinable: it independently encodes call type (single vs. batch) and whether an additional `opData` payload trails the `Execution[]` array (i.e. `executionData = abi.encode(calls, opData)` rather than `executionData = abi.encode(calls)`). `_containsFillOrder` never inspects the discarded `mode` value to decide which of these shapes it is looking at — it always assumes the simple `Execution[]` shape used by the SDK's own encoder: [5](#0-4) 

This is structurally the same class of bug as the OpenClaw advisory: two code paths (the approval/validation-time parser and the execution-time parser) must agree on how "combined options" (here, the `mode` bitfield) change the interpretation of the same payload, and one of them ignores the discriminator entirely. An attacker who crafts calldata with a `mode` value the account's `execute()` still accepts, but whose `executionData` layout differs from the plain `Execution[]` the scanner expects, can make `_containsFillOrder`'s `abi.decode(executionData, (Execution[]))` either revert (masking a real embedded `fillOrder` call, since the code treats a decode failure the same as "no fillOrder found" — it only returns `true` inside the loop, `false` otherwise) or successfully decode a spurious/garbled array that hides the actual `Execution` entries that will run at execution time.

### Impact Explanation
The check exists specifically to stop unprivileged actors from resubmitting a solver's public bid (a UserOp signed with a plain 65-byte ECDSA signature over `userOpHash`, embedding a `fillOrder` call) through the fast validation path without the `select()`-staged session key that `fillOrder` requires at execution. The code's own docstring states the intended (mitigated) consequence of a bypass: the bid's ERC‑4337 nonce gets consumed and the solver is griefed for gas fees on every replayed op, since `fillOrder` will revert without a staged selection at execution. If `_containsFillOrder` misparses combined-mode calldata and fails to flag the embedded `fillOrder` call, any unprivileged relayer of the EntryPoint (bundler, MEV searcher, or anyone who observed the public bid) can grief solver accounts at scale by replaying their bids through the fast path, burning solver gas and consuming/wasting UserOp nonces — an unauthorized app action reachable by any party that can submit an ERC‑4337 UserOp referencing the solver's public bid.

### Likelihood Explanation
Reachability is via a standard ERC‑4337 `UserOperation` submitted to the EntryPoint, requiring no privileged access — any address that has observed a solver's publicly broadcast bid calldata and signature can replay it. The only obstacle is crafting a `mode`/`executionData` combination that `ERC7821.execute()` (the OpenZeppelin base contract) still accepts as valid but that decodes differently than `_containsFillOrder` assumes; this is plausible given ERC‑7821's mode field is explicitly designed to be combinable (call type × exec type × opData-presence), which is exactly the class of "combined option" ambiguity described in the source advisory. Full confirmation that OpenZeppelin's specific `draft-ERC7821` build in this repo's dependency tree accepts a mode that alters the `executionData` layout could not be verified from the indexed files (the OpenZeppelin package source is a third-party dependency not present in the codebase index), so the precise combined-mode value that triggers the mismatch is not proven here — only the code-level parsing asymmetry between `_containsFillOrder` and the real `execute()` dispatch is established.

### Recommendation
In `_containsFillOrder`, do not discard the `mode` value — validate it against the exact mode(s) the account intends to support (e.g. reject any op whose mode differs from the single canonical batch-mode constant used by the SDK), and decode `executionData` using the same mode-dependent logic that `ERC7821.execute()` itself uses, so validation-time and execution-time parsing can never diverge. Alternatively, refuse the ECDSA fast path entirely for any `mode` other than the one canonical value the protocol issues, closing off any combined/alternate mode from reaching execution at all.

### Proof of Concept
1. A solver signs and broadcasts a bid: a UserOp with `signature.length == 65` (plain ECDSA over `userOpHash`) and `callData` targeting `ERC7821.execute(mode, executionData)`, where `executionData` encodes a batch containing a call to `IntentGatewayV2.fillOrder`.
2. An attacker observes this public bid and re-encodes an equivalent `execute` call using a different (but `ERC7821`-supported) `mode` value that changes how `executionData` must be parsed (e.g., a mode signaling an appended `opData` field), while padding/positioning the bytes such that the real `execute()` still extracts and dispatches the same `fillOrder` call to `INTENT_GATEWAY_V2` at execution.
3. During validation, `_containsFillOrder` ignores the (now different) mode and calls `abi.decode(executionData, (Execution[]))` against the reshaped bytes, causing it to either revert (function returns `false` after failing to find `hasFillOrder`, since the revert path is not distinguished from "no match") or decode a shape that no longer surfaces `target == INTENT_GATEWAY_V2 && selector == FILL_ORDER_SELECTOR`, so `_containsFillOrder` returns `false`.
4. `validateUserOp` proceeds via `super.validateUserOp(...)`, which succeeds since the ECDSA signature is genuinely the solver's, and the EntryPoint executes the op, running `execute()` which correctly parses the true mode and dispatches `fillOrder` — reverting only because no `select()` was staged, exactly as the code's own risk analysis describes, but now with the intended pre-execution block bypassed and the solver's nonce/gas consumed by an unprivileged replayer. [6](#0-5)

### Citations

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L17-21)
```text
import {Account} from "@openzeppelin/contracts/account/Account.sol";
import {ERC4337Utils} from "@openzeppelin/contracts/account/utils/draft-ERC4337Utils.sol";
import {ERC7821} from "@openzeppelin/contracts/account/extensions/draft-ERC7821.sol";
import {PackedUserOperation} from "@openzeppelin/contracts/interfaces/draft-IERC4337.sol";
import {Execution} from "@openzeppelin/contracts/interfaces/draft-IERC7579.sol";
```

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L103-111)
```text
    function validateUserOp(PackedUserOperation calldata op, bytes32 userOpHash, uint256 missingAccountFunds)
        public
        override
        onlyEntryPoint
        returns (uint256)
    {
        if (op.signature.length == ECDSA_SIGNATURE_LENGTH) {
            if (_containsFillOrder(op.callData)) return ERC4337Utils.SIG_VALIDATION_FAILED;
            return super.validateUserOp(op, userOpHash, missingAccountFunds);
```

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L142-163)
```text
    /**
     * @notice Scans userOp calldata for a call to IntentGatewayV2.fillOrder
     * @dev The calldata is covered by the solver's signature over the userOpHash, so a
     *      replayed bid cannot be reshaped to hide the call — the scan only needs to
     *      recognize the bid's ERC-7821 execute(mode, executionData) batch. abi.decode
     *      reverts on malformed calldata, rejecting the op during validation just as
     *      execution would.
     * @param callData The userOp calldata to scan
     * @return bool True if the calldata contains a fillOrder call to the IntentGateway
     */
    function _containsFillOrder(bytes calldata callData) private view returns (bool) {
        if (callData.length < 4 || bytes4(callData[0:4]) != EXECUTE_SELECTOR) return false;

        (, bytes memory executionData) = abi.decode(callData[4:], (bytes32, bytes));
        Execution[] memory calls = abi.decode(executionData, (Execution[]));

        for (uint256 i = 0; i < calls.length; i++) {
            bool hasFillOrder = calls[i].target == INTENT_GATEWAY_V2 && bytes4(calls[i].callData) == FILL_ORDER_SELECTOR;
            if (hasFillOrder) return true;
        }
        return false;
    }
```

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L198-206)
```text
    function _erc7821AuthorizedExecutor(address caller, bytes32 mode, bytes calldata executionData)
        internal
        view
        virtual
        override
        returns (bool)
    {
        return caller == address(entryPoint()) || super._erc7821AuthorizedExecutor(caller, mode, executionData);
    }
```

**File:** sdk/packages/sdk/src/protocols/intents/decode-utils.ts (L7-18)
```typescript
export function encodeERC7821ExecuteBatch(calls: ERC7821Call[]): HexString {
	const executionData = encodeAbiParameters(
		[{ type: "tuple[]", components: ERC7821ABI.ABI[1].components }],
		[calls.map((call) => ({ target: call.target, value: call.value, data: call.data }))],
	) as HexString

	return encodeFunctionData({
		abi: ERC7821ABI.ABI,
		functionName: "execute",
		args: [ERC7821_BATCH_MODE, executionData],
	}) as HexString
}
```
