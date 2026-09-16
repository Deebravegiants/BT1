## Title
`SolverAccount._containsFillOrder` scans one assumed ERC-7821 calldata shape while `execute()` may dispatch a different one, letting a `fillOrder` bid bypass the griefing guard - ([File: evm/src/apps/intentsv2/SolverAccount.sol])

### Summary
The external report's root cause is generic: a security-relevant check is implemented against an *assumed* representation of the operation (`msg.flags` at the EVMC host layer) that a different code path (the VM's `CREATE`/`CREATE2` opcode handler) never actually populates, so the guard silently never fires. The candidate analog in Hyperbridge is `SolverAccount._containsFillOrder` (`evm/src/apps/intentsv2/SolverAccount.sol:152-163`), which decides whether a standard-ECDSA `PackedUserOperation` is allowed to execute by decoding `op.callData` under one fixed assumption — that it is an ERC-7821 `execute(mode, executionData)` call whose `executionData` ABI-decodes as `Execution[]` — and rejecting anything that fails that specific shape only when a `fillOrder` selector is found inside it.

### Finding Description
`validateUserOp` (`evm/src/apps/intentsv2/SolverAccount.sol:103-140`) takes the "standard 65-byte ECDSA" branch when `op.signature.length == ECDSA_SIGNATURE_LENGTH`, and gates it solely with:
```solidity
if (_containsFillOrder(op.callData)) return ERC4337Utils.SIG_VALIDATION_FAILED;
return super.validateUserOp(op, userOpHash, missingAccountFunds);
```
`_containsFillOrder` (lines 152-163) hard-codes a single decode path:
```solidity
if (callData.length < 4 || bytes4(callData[0:4]) != EXECUTE_SELECTOR) return false;
(, bytes memory executionData) = abi.decode(callData[4:], (bytes32, bytes));
Execution[] memory calls = abi.decode(executionData, (Execution[]));
for (...) { if (calls[i].target == INTENT_GATEWAY_V2 && bytes4(calls[i].callData) == FILL_ORDER_SELECTOR) return true; }
```
This mirrors the `evmc_host.hpp` situation precisely: a security gate that is coded against one specific encoding of the operation (batch-call `Execution[]`), while the *actual* dispatcher that will execute the calldata — OpenZeppelin's `ERC7821.execute(bytes32 mode, bytes executionData)` — is a mode-driven dispatcher (ERC-7579-style `callType`/`execType` fields packed into the leading bytes of `mode`) that can route the same selector to differently-shaped `executionData` (e.g., a single-call mode whose payload is a single `(address,uint256,bytes)` tuple rather than an array, or a "try/no-revert" execution type). If any mode variant that `ERC7821.execute` accepts is decoded by `_containsFillOrder` in a way that doesn't line up 1:1 with what `execute()` will actually dispatch — either causing the scanner's `abi.decode` to silently succeed on a mis-parsed structure instead of reverting, or to genuinely fail to recognize an equivalent call to `fillOrder` — the guard is bypassed exactly the way `msg.flags & EVMC_DELEGATED` was always zero: the check exists in source but is checking the wrong representation of the operation that will actually run.

I could not fully verify the exact set of modes `ERC7821.execute` accepts in this codebase's vendored OpenZeppelin version (the `draft-ERC7821.sol` source was not present in the indexed context, so I cannot confirm with certainty which specific mode value(s), if any, produce a decode mismatch in the current dependency pin). This is the key uncertainty in this analog: without the OZ `ERC7821` execute() implementation on hand, I cannot prove a concrete mode value that both (a) `execute()` accepts and dispatches to a live `fillOrder` call, and (b) causes `_containsFillOrder`'s fixed `abi.decode(executionData, (Execution[]))` to either revert (safe) or succeed with a payload that fails the `calls[i].target == INTENT_GATEWAY_V2 && bytes4(calls[i].callData) == FILL_ORDER_SELECTOR` match despite `fillOrder` executing.

### Impact Explanation
If such a mode mismatch exists, the impact matches the underlying comment in the file itself: bids are public and carry a valid 65-byte solver signature over the `userOpHash`. An attacker who strips the commitment/session signature from a public bid and resubmits the raw calldata through a mode that `_containsFillOrder` fails to recognize would pass validation, consuming the bid's nonce and charging the solver's gas / griefing the solver — exactly the scenario the guard exists to prevent (see the docstring at lines 84-88 and the dedicated regression test `test_ValidateUserOp_StandardECDSA_FillOrderCalldata_Fails` in `evm/tests/foundry/account/SolverAccountTest.sol:151-170`). This is medium/high severity griefing against an unprivileged solver/relayer's funds via gas consumption and forced nonce burn, reachable from a single crafted `PackedUserOperation` — squarely within scope (intent solver path).

### Likelihood Explanation
Likelihood is uncertain and cannot be elevated to "confirmed" without the vendored `ERC7821.execute()` source to check whether any accepted mode actually produces the described decode mismatch. If OpenZeppelin's `ERC7821` in this dependency only implements the single "batch call" mode (calltype 0x01) and reverts on any other mode, then this is not exploitable and the guard is sound. The pattern is structurally identical to the reported bug class (a check keyed to one representation of an operation that a separate dispatcher may not honor), but I do not have concrete proof of a bypassable mode in this specific OZ version.

### Recommendation
- Do not re-implement calldata scanning against an assumed ABI shape. Instead, enforce the guard at the point where `fillOrder` actually executes (e.g. a `nonReentrant`/one-shot check inside `IntentGatewayV2.fillOrder` itself gated on whether a `select()` was staged in the same transaction), mirroring the report's own recommendation to "shift the check to the VM layer" rather than to the caller-supplied representation.
- If the scan approach is kept, explicitly enumerate and reject every `mode` value not equal to the single supported batch-call mode before attempting to decode `executionData`, rather than only checking the outer selector.
- Add a regression test that submits `execute()` calldata under every `mode`/`callType` value that OpenZeppelin's `ERC7821.execute` accepts (single call, batch call, and any "try"/no-revert execution type), each wrapping a `fillOrder` call, and assert that `validateUserOp` rejects all of them.

### Proof of Concept
Not constructed — this requires confirming the vendored `ERC7821.execute()` mode-dispatch logic (source not found in the indexed context) to identify a concrete `mode` value that (a) `execute()` accepts and forwards to `fillOrder`, and (b) is mis-decoded or unrecognized by `_containsFillOrder`. Absent that confirmation, treat this as a **candidate** analog requiring source verification of the exact OpenZeppelin `ERC7821` version pinned by `evm/package.json`, rather than a proven exploit. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L103-140)
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

        // Expected format: abi.encodePacked(commitment, solverSignature, sessionSignature)
        // commitment: 32 bytes, solverSignature: 65 bytes, sessionSignature: 65 bytes
        if (op.signature.length < INTENT_SELECT_SIGNATURE_LENGTH) return ERC4337Utils.SIG_VALIDATION_FAILED;

        bytes32 commitment = bytes32(op.signature[0:32]);
        bytes calldata solverSignature = op.signature[32:97];
        bytes calldata sessionSignature = op.signature[97:162];

        // Call IntentGatewayV2.select to recover the sessionKey. This also stages the
        // transient-storage selection that fillOrder enforces at execution.
        SelectOptions memory selectOptions =
            SelectOptions({commitment: commitment, solver: address(this), signature: sessionSignature});
        bytes memory selectCalldata = abi.encodeWithSelector(SELECT_SELECTOR, selectOptions);
        (bool success, bytes memory returnData) = INTENT_GATEWAY_V2.call(selectCalldata);

        if (!success || returnData.length < 32) return ERC4337Utils.SIG_VALIDATION_FAILED;

        address sessionKey = abi.decode(returnData, (address));
        uint192 userOpNonce = uint192(uint256(keccak256(abi.encodePacked(commitment, sessionKey))));
        if (uint192(op.nonce >> 64) != userOpNonce) return ERC4337Utils.SIG_VALIDATION_FAILED;
        if (!_rawSignatureValidation(userOpHash, solverSignature)) return ERC4337Utils.SIG_VALIDATION_FAILED;

        // Pay for gas if needed
        _payPrefund(missingAccountFunds);

        return ERC4337Utils.SIG_VALIDATION_SUCCESS;
    }
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

**File:** evm/tests/foundry/account/SolverAccountTest.sol (L151-170)
```text
    /// @dev The fast path must refuse fillOrder calldata: bids are public and embed a
    ///      valid 65-byte solver signature over the userOpHash, so anyone could strip
    ///      the commitment and session signature from a bid and submit the op with it.
    ///      The fill would revert (no selection staged during validation), but the
    ///      bid's nonce would be consumed and the solver griefed of the gas fees.
    function test_ValidateUserOp_StandardECDSA_FillOrderCalldata_Fails() public {
        bytes32 userOpHash = keccak256("test_userop");

        Execution[] memory calls = new Execution[](1);
        calls[0] = Execution({
            target: address(intentGateway), value: 0, callData: abi.encodeWithSelector(intentGateway.fillOrder.selector)
        });

        PackedUserOperation memory op = _standardOp(_executeCalldata(calls), _signUserOpHash(userOpHash));

        vm.prank(entryPoint);
        uint256 result = solverAccount.validateUserOp(op, userOpHash, 0);

        assertEq(result, ERC4337Utils.SIG_VALIDATION_FAILED);
    }
```
