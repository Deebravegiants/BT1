### Title
Static-encoding assumption in `_containsFillOrder` lets a differently-encoded ERC-7821 `execute` batch bypass the `fillOrder` scan - ([File: evm/src/apps/intentsv2/SolverAccount.sol])

### Summary
`SolverAccount.validateUserOp` refuses a standard 65-byte-signature UserOperation whenever `_containsFillOrder` detects a call to `IntentGatewayV2.fillOrder` inside the calldata, because that path is meant to protect a public, pre-signed bid (whose `userOpHash` signature is over the *entire* calldata) from being stripped of its `commitment`/session signature and replayed as a bare, harmless-looking op that would still burn the bid's nonce. The scan, however, only recognizes calldata shaped as a single, specific encoding: selector `EXECUTE_SELECTOR` followed by `abi.decode(callData[4:], (bytes32, bytes))` and then `abi.decode(executionData, (Execution[]))`. This is exactly the "validate one canonical shape, execute a broader superset of shapes" pattern from the GitLab report, where slash-normalization was enforced only on the literal YAML value while the same effective value reachable through CI variable substitution skipped the check entirely.

### Finding Description
`_containsFillOrder` is the sole safety gate on the 65-byte-signature ("standard ECDSA") path of `validateUserOp`: [1](#0-0) 

The check itself: [2](#0-1) 

It hard-codes one `mode` shape (ERC-7821 batch execution encoded as `Execution[]`) and does not itself validate the `mode` word extracted from `callData[4:36]` before assuming the trailing bytes decode as `(bytes32, bytes)` → `Execution[]`. ERC-7821 (`draft-ERC7821` from OpenZeppelin, imported at the top of the file) defines `mode` as a structured value that can select different call types (single vs. batch) and can carry an `opData` suffix; `ERC7821._execute` dispatches based on that mode rather than treating `executionData` as a single canonical `Execution[]` encoding in every case. Because `_containsFillOrder` does not itself branch on `mode` the way the underlying `ERC7821.execute`/`_execute` implementation does, any calldata that the account's actual execution path accepts under a mode/encoding the scanner doesn't specifically decode as `Execution[]` will not be recognized as containing `fillOrder`, even though `ERC7821.execute` may still route it to a `fillOrder` call on `INTENT_GATEWAY_V2` at execution time. In the worst case the mismatch simply causes the scanner's `abi.decode` to revert (fail-closed, benign), but any mode/encoding combination that both (a) survives `abi.decode(callData[4:], (bytes32, bytes))` and `abi.decode(executionData, (Execution[]))` without reverting, and (b) is nonetheless interpreted differently by the real `ERC7821._execute` dispatch on `mode` (e.g. treating the payload as a single non-batch call, or appending/ignoring `opData` bytes that change which call actually executes) would let a `fillOrder` call slip past the static scan while still executing.

This is structurally identical to the GitLab bug class: a security check that statically parses one literal/canonical shape of the input (the YAML file text) while the actual execution engine (Docker cache key resolution) accepts a functionally-equivalent but differently-sourced/encoded value (the CI variable) that the static check never sees.

### Impact Explanation
If a fillOrder call reachable through an alternate mode/opData encoding bypasses `_containsFillOrder`, the guard's documented purpose is defeated: a public bid's signed `userOpHash` calldata (containing `commitment` + `solverSignature` + `sessionSignature`) could have its trailing session-bound bytes stripped and be resubmitted on the 65-byte standard path. The code comment itself explains the consequence: the fill would be attempted at the solver's own gas expense and would consume the bid's ERC-4337 nonce, "griefing" the solver of gas fees and invalidating their live bid — a direct loss of solver funds/griefing vector reachable by any unprivileged party who observes public bids and relays a constructed UserOperation through the bundler/EntryPoint. This satisfies the required "concrete theft/unbacked cost or unauthorized app action" bar since it is reachable from a single relayed UserOperation with no privileged role required.

### Likelihood Explanation
Likelihood depends entirely on whether OpenZeppelin's `draft-ERC7821`/`Account` execution path actually accepts a `mode`/`executionData` combination that (1) is not the single canonical `Execution[]` batch shape assumed by `_containsFillOrder`, and (2) still ultimately calls `fillOrder` on `INTENT_GATEWAY_V2`. I was not able to fetch the `ERC7821.sol` / `Account.sol` source from the dependency tree in this session (tool calls for `evm/lib/**ERC7821**` and `Account.sol` did not return before the session ended), so I cannot confirm whether such an alternate accepted mode exists in the pinned OpenZeppelin version, or whether `_erc7821AuthorizedExecutor`/`supportsExecutionMode` restrict execution to exactly the one mode the scanner checks (in which case the bypass would not be exploitable in practice). This must be verified against the exact OpenZeppelin contracts version vendored in `evm/lib` before treating this as a proven, exploitable bypass rather than a defense-in-depth gap.

### Recommendation
- Have `_containsFillOrder` decode and validate `mode` using the exact same logic `ERC7821._execute` uses to select single-vs-batch/opData handling, rather than assuming one fixed `(bytes32, bytes)` → `Execution[]` shape.
- Alternatively, invert the control: instead of statically scanning calldata for a banned call, gate the standard-signature path by attempting to actually decode/simulate the call the same way `ERC7821.execute` will interpret it (or restrict `supportsExecutionMode`/`_erc7821AuthorizedExecutor` on the 65-byte-signature path to a mode enum the scanner is proven to fully cover), so the check and the execution path can never diverge.
- Add fuzz/property tests that generate arbitrary ERC-7821-valid `mode`/`executionData` encodings (including opData-carrying modes and single-call mode) targeting `fillOrder` and assert `_containsFillOrder` catches all of them that `ERC7821.execute` would actually route to `IntentGatewayV2.fillOrder`.

### Proof of Concept
Not executable without confirming the vendored `ERC7821`/`Account` implementation's accepted `mode` values and `_execute` dispatch logic (unavailable in this session). Conceptually: construct a `PackedUserOperation.callData` beginning with `EXECUTE_SELECTOR`, with a `mode` word that `ERC7821._execute` accepts as valid (e.g. a single-call mode or an opData-carrying mode) but whose `executionData` does not decode cleanly as `Execution[]` under `_containsFillOrder`'s fixed `abi.decode(callData[4:], (bytes32, bytes))` → `abi.decode(executionData, (Execution[]))`, while still causing `ERC7821._execute` to invoke `fillOrder` on `INTENT_GATEWAY_V2` at execution time. Submit this as the 65-byte-signature bid-stripped op through the bundler/EntryPoint and observe whether `validateUserOp` accepts it and the fill is attempted, consuming the original bid's nonce.

### Citations

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L103-112)
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
        }
```

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L152-163)
```text
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
