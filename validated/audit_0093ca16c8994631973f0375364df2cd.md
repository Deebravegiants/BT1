## Title
`SolverAccount` derives security-critical selectors from a declaration-only interface that has no compile-time link to the real `IntentGatewayV2` implementation - ([File: evm/src/apps/intentsv2/SolverAccount.sol])

### Summary
The JOJO report's root cause — a contract that is *assumed* to satisfy an interface but does not actually implement/match it, causing a reachable call in a critical path to silently fail or behave incorrectly — has a direct analog in `SolverAccount.sol`. It caches `bytes4` selectors from `IIntentGatewayV2` (a declaration-only interface with no compiler-enforced relationship to the deployed `IntentGatewayV2` contract) and uses them both to invoke the gateway and to police a security-relevant scan of user-operation calldata. There is no Solidity-level guarantee that these selectors match the real, deployed `IntentGatewayV2`.

### Finding Description
`SolverAccount` imports `IIntentGatewayV2` purely for its function selectors: [1](#0-0) 

The actual gateway (`evm/src/apps/IntentGatewayV2.sol`) does **not** inherit from this interface — it is a separate, hand-maintained "published ABI surface" file living in the `sdk/packages/core` package, kept in sync with the real implementation only by manual diffing, as the repo's own engineering notes admit: [2](#0-1) 

and: [3](#0-2) 

`SELECT_SELECTOR` is used to call the live gateway during `validateUserOp` — exactly the "call an interface function that the target doesn't actually expose" pattern from the JOJO report: [4](#0-3) 

`FILL_ORDER_SELECTOR` is used to detect (and block) a `fillOrder` call hidden inside a batched ERC-7821 execution, which is the account's defense against a specific griefing/bid-replay attack described in the code's own comments: [5](#0-4) [6](#0-5) 

Because nothing compiles `IntentGatewayV2` against `IIntentGatewayV2` (no `is IIntentGatewayV2` anywhere), a future signature change to `select()` or `fillOrder()` in the real gateway — without an equal and opposite update to the declaration-only interface — is invisible to the Solidity compiler, exactly as `OracleAdaptorWstETH` was allowed to omit `getMarkPrice()` from `IPriceSource` without a build failure.

### Impact Explanation
- If `SELECT_SELECTOR` drifts from the real `select()` selector, `INTENT_GATEWAY_V2.call(selectCalldata)` fails at line 127, `validateUserOp` always returns `SIG_VALIDATION_FAILED`, and every solver-selection-based user operation is permanently unable to validate — a denial of service for the entire intent-solver delegation flow reachable by any relayer/bundler submitting a user operation.
- If `FILL_ORDER_SELECTOR` drifts, `_containsFillOrder` silently fails to recognize genuine `fillOrder` calls embedded in a batch, defeating the exact griefing protection the function exists to enforce (documented in the contract itself): an attacker can strip a public bid's commitment/session signature and replay it through the plain-ECDSA validation path, consuming the solver's nonce and burning the solver's gas — a direct, unprivileged fund-loss vector against solvers.

### Likelihood Explanation
The two signature sets are currently kept manually synchronized ("brought back in sync"), meaning the vulnerability is latent rather than actively exploited today, but the structural defect — a security check whose correctness depends on two independently-maintained files staying byte-identical with zero compiler enforcement — is exactly the class of bug the JOJO report flags. Any future, unrelated change to `evm/src/apps/IntentGatewayV2.sol`/`IntentsBase.sol` (e.g. a parameter reorder in `select`/`fillOrder`) that is not mirrored in `sdk/packages/core/contracts/apps/IntentGatewayV2.sol` reintroduces the failure with no build-time signal, and is only caught by manual diffing per the repo's own admission.

### Recommendation
Remove the duplicate declaration-only interface as the source of truth for selectors used in security logic. Either:
1. Have `IntentGatewayV2` explicitly `is IIntentGatewayV2` so the compiler enforces conformance, or
2. Have `SolverAccount` import the real gateway's interface/ABI directly (not a hand-copied duplicate) so `select.selector` and `fillOrder.selector` are derived from the actual implementation, eliminating the possibility of silent drift.

### Proof of Concept
Not applicable as a live exploit against current code (selectors are presently in sync per repo history); the finding is a structural/root-cause analog validated by direct code and documentation inspection of `SolverAccount.sol`, `IIntentGatewayV2` declarations, and the repository's own AI-authored decision/flow notes acknowledging the unenforced duplication.

### Citations

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L48-60)
```text
     * @notice Cached select function selector
     */
    bytes4 private constant SELECT_SELECTOR = IIntentGatewayV2.select.selector;

    /**
     * @notice Cached fillOrder function selector
     */
    bytes4 private constant FILL_ORDER_SELECTOR = IIntentGatewayV2.fillOrder.selector;

    /**
     * @notice Cached ERC-7821 execute function selector
     */
    bytes4 private constant EXECUTE_SELECTOR = ERC7821.execute.selector;
```

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L78-94)
```text
    /**
     * @notice Validates a user operation before execution
     * @dev Two modes, discriminated by signature length:
     *
     * 1. Standard ECDSA (65 bytes): validated by the Account base contract against
     *    the plain userOpHash. Refused if the calldata contains a fillOrder call to
     *    the IntentGateway: bids are public and embed a valid 65-byte solver signature
     *    over the userOpHash, so anyone could strip the commitment and session
     *    signature from a bid and submit the op on this path. Without a select()
     *    staged during validation the fill reverts, but the bid's nonce would be
     *    consumed and the solver griefed of the gas fees.
     * 2. Intent solver selection (162 bytes): abi.encodePacked(commitment,
     *    solverSignature, sessionSignature). The solver signs the plain userOpHash,
     *    and the userOp's nonce key must equal the lower 192 bits of
     *    keccak256(abi.encodePacked(commitment, sessionKey)) — binding the operation
     *    to the order and the session key it was bid against, so neither can be
     *    swapped after signing.
```

**File:** evm/src/apps/intentsv2/SolverAccount.sol (L122-129)
```text
        // Call IntentGatewayV2.select to recover the sessionKey. This also stages the
        // transient-storage selection that fillOrder enforces at execution.
        SelectOptions memory selectOptions =
            SelectOptions({commitment: commitment, solver: address(this), signature: sessionSignature});
        bytes memory selectCalldata = abi.encodeWithSelector(SELECT_SELECTOR, selectOptions);
        (bool success, bytes memory returnData) = INTENT_GATEWAY_V2.call(selectCalldata);

        if (!success || returnData.length < 32) return ERC4337Utils.SIG_VALIDATION_FAILED;
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

**File:** sdk/packages/core/docs/ai/decisions/2026-08-27-declarations-here-are-kept-identical-to-intentsbase-not-merely.md (L1-9)
```markdown
# 2026-08-27 — Declarations here are kept identical to `IntentsBase`, not merely compatible

Chosen: every event and error in `IIntentGatewayV2` matches `evm/src/apps/intentsv2/IntentsBase.sol`
exactly — same name, same parameter types, same `indexed` flags.

Nothing compiles against these declarations (`SolverAccount.sol` uses the interface only for two
function selectors), so a mismatch produces no build error anywhere in the repo. That is exactly
why the drift went unnoticed through several signature changes. The only thing that can catch it
is the rule that the two lists are equal, which is cheap to check by diffing them.
```

**File:** sdk/packages/core/docs/ai/flows/what-iintentgatewayv2-is-and-what-actually-reads-it.md (L8-20)
```markdown
Two consumers, and they use it very differently:

1. **`evm/src/apps/intentsv2/SolverAccount.sol`** imports it and reads exactly two things:
   `IIntentGatewayV2.select.selector` and `IIntentGatewayV2.fillOrder.selector`. It resolves via the
   `@hyperbridge/core/` remapping in `evm/remappings.txt`, which points at
   `node_modules/@hyperbridge/core/contracts/` — a workspace symlink, so an edit here is picked up
   by `forge build` in `evm/` with no publish step. Only the two function signatures matter to it.
2. **Integrators**, who read the file as the gateway's published ABI surface. Everything else in it
   — the events especially — exists for them alone.

That split is the whole reason the events drift: nothing in the repo compiles against them, so a
wrong signature is silent locally and only wrong for whoever depends on the package. The
declaration lists in this file and in `IntentsBase.sol` are kept identical; diffing them is the
```
