### Title
`SolverAccount._containsFillOrder` blindly decodes ERC-7821 `executionData` as a batch, letting a stripped bid's `fillOrder` call bypass the anti-griefing scan - (File: `evm/src/apps/intentsv2/SolverAccount.sol`)

### Summary
The external report's bug class is "a security check decodes attacker-controlled bytes with different alignment/format assumptions than the component that actually executes them, letting a malicious payload sail through the check but still perform the guarded action." `SolverAccount._containsFillOrder` reproduces this exact shape: it re-parses `op.callData` under a single hard-coded assumption (batch-mode `execute(bytes32 mode, bytes executionData)` → `abi.decode(executionData,(Execution[]))`), while ERC-7821 (Solady's base contract, imported but not vendored in this repo) actually branches its real decoding on the `mode` value itself, supporting several call-type encodings (single call, batch call, batch call with opData, delegatecall, etc.). The scan never validates `mode` before assuming the batch shape.

### Finding Description
`SolverAccount.validateUserOp` takes the fast (65-byte ECDSA) signature path only if `_containsFillOrder(op.callData)` returns `false`: [1](#0-0) 

`_containsFillOrder` is the entire guard: [2](#0-1) 

It checks the selector is `EXECUTE_SELECTOR` and then unconditionally does:
```
(, bytes memory executionData) = abi.decode(callData[4:], (bytes32, bytes));
Execution[] memory calls = abi.decode(executionData, (Execution[]));
```
It discards the decoded `mode` (bytes32) entirely — it never checks that `mode` is the standard ERC-7821 "batch of calls, revert on failure" mode. The real `execute()` implementation inherited from `ERC7821` (Solady), however, dispatches on `mode` to choose among different `executionData` layouts (single-call opdata vs. batch-of-`Execution[]` vs. delegatecall variants) — this is the whole point of the ERC-7821 mode byte. Because the scan hard-codes "always decode as `Execution[]`" without confirming `mode` matches what the executor will actually use, an attacker who crafts `op.callData` with a `mode` value that (a) the real executor interprets as a single call to `IntentGatewayV2.fillOrder`, but (b) the scanner's blind `abi.decode(executionData, (Execution[]))` either reverts on, is caught by Solidity's `try/catch`-less top-level call semantics, or – more importantly – decodes to a struct whose `.target` / `.callData` slots do not line up with `INTENT_GATEWAY_V2` / `FILL_ORDER_SELECTOR` even though the *actual* execution routes to `fillOrder`, causes `hasFillOrder` to stay `false`.

This mirrors the Forta report precisely: the "scam-detector" (`_containsFillOrder`) and the "real interpreter" (Solady's `execute`) disagree on how to parse the same bytes because the scan makes an alignment/format assumption (`mode` is always the batch mode, hence `executionData` is always `Execution[]`) that isn't enforced, exactly like the report's ABI-encoder disagreement over trailing zero bytes.

### Impact Explanation
If this decode mismatch is exploitable (i.e., there exists a `mode`/`executionData` pairing that the real `ERC7821.execute` interprets as calling `IntentGatewayV2.fillOrder(...)` but that `_containsFillOrder`'s hard-coded `Execution[]` decode does not flag), an attacker can strip the `commitment`/`sessionSignature` bytes from a publicly-visible solver bid (bids and their 65-byte `solverSignature` over `userOpHash` are public on Hyperbridge per the code's own comments) and resubmit it through the standard ECDSA fast path. As documented directly in the code (`evm/src/apps/intentsv2/SolverAccount.sol:83-88`), this is exactly the attack the guard exists to stop: the fill itself reverts (no `select()` staged in validation), but the bid's ERC-4337 nonce is consumed and the legitimate solver is griefed out of gas and their winning bid slot — a denial-of-service / griefing vector against solvers that undermines the intent-fill auction's integrity (Medium severity: griefing/DoS on solver funds and auction fairness rather than direct fund theft).

### Likelihood Explanation
Likelihood depends entirely on whether Solady's `ERC7821.execute` truly diverges from `_containsFillOrder`'s single fixed assumption for some legal `mode` value that still results in a call to `fillOrder` on `INTENT_GATEWAY_V2`. I could not verify Solady's exact mode-dispatch table inside this repository — `ERC7821` is imported but not vendored/found by search, so I cannot confirm with certainty that a mode/executionData pairing exists that both (a) the real executor treats as a valid call to `fillOrder`, and (b) `_containsFillOrder`'s hard-coded `abi.decode(executionData, (Execution[]))` fails to recognize. This uncertainty should be treated as the key item to verify before treating this as confirmed-exploitable rather than a plausible analog.

### Recommendation
- In `_containsFillOrder`, validate that the decoded `mode` equals the exact standard batch-execution mode constant (`ERC7821_BATCH_MODE`, already defined elsewhere in the SDK at `sdk/packages/sdk/src/protocols/intents/CryptoUtils.ts`) before trusting the `Execution[]` decode; if `mode` is anything else, conservatively treat the calldata as "contains fillOrder" (fail closed) rather than "does not contain fillOrder" (fail open).
- Alternatively, drive the scan off the same decoding function the base `ERC7821` contract uses internally (e.g., call a shared internal helper instead of re-implementing decode logic in `_containsFillOrder`), so the two can never diverge.
- Add fuzz/unit tests that construct `execute()` calldata using every `mode` variant Solady's ERC7821 supports and assert `_containsFillOrder` returns `true` whenever the resulting real execution would call `fillOrder` on `INTENT_GATEWAY_V2`, closing the same class of bug the size-check patch closed in the referenced Forta report.

### Proof of Concept
Not independently reproducible from the indexed code alone: exploiting this requires the precise Solady `ERC7821` mode-dispatch semantics (not present in this repo's indexed sources) to construct a `mode`/`executionData` pair that (1) `execute()` actually routes to `IntentGatewayV2.fillOrder`, and (2) `abi.decode(executionData, (Execution[]))` in `_containsFillOrder` does not detect it. This should be validated with a live Foundry test against the vendored Solady `ERC7821` implementation (e.g., extending `evm/tests/foundry/account/SolverAccountTest.sol`) before treating the bypass as confirmed.

### Citations

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L109-112)
```text
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
