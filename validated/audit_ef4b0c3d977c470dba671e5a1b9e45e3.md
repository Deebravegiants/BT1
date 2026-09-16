### Title
Malicious destination module can permanently revert an entire relayed batch, burning relayer gas and freezing delivery of unrelated messages - (File: `evm/src/core/HandlerV2.sol`)

### Summary
`HandlerV2::handlePostRequests` and `HandlerV2::handleGetResponses` verify a Merkle Mountain Range multiproof for an entire batch of leaves in one call, and then iterate over every leaf, unconditionally calling `host.dispatchIncoming(...)` for each one with no isolation (no try/catch, no gas-capped low-level call). This mirrors the zkSync bootloader pattern where `nearCallPanic()` is used for a call whose failure is fully attacker/operator-influenced: here, a single destination application that always reverts (or intentionally burns all forwarded gas) on its `IApp` callback causes the *entire* batched transaction — including proof verification work for every unrelated, honest request/response in the batch — to revert.

### Finding Description
`handlePostRequests` builds one `MerkleMountainRange` proof covering `requestsLen` leaves and validates it in a single call: [1](#0-0) 

It then loops and dispatches every leaf directly to the destination module via `host.dispatchIncoming`, with no error containment around that external call: [2](#0-1) 

The identical pattern exists for GET responses: [3](#0-2) 

Because `dispatchIncoming` ultimately invokes the destination `IApp`'s callback (`onAccept`/response handler) and that callback is neither wrapped in `try/catch` nor capped to a fixed gas stipend at the Handler layer, any destination application that is designed (or buggy) to revert unconditionally, run out of gas, or consume unbounded gas will bubble that failure up through `dispatchIncoming` and revert the *whole* `handlePostRequests`/`handleGetResponses` call. This is architecturally identical to the zkSync bootloader's `sendCompressedBytecode`/`nearCallPanic` issue: a single untrusted sub-call embedded inside a larger batched operation is allowed to unconditionally fail the entire batch, wasting all the gas spent on unrelated, valid work (merkle proof verification, timeout/duplicate checks for every other leaf in the batch).

`IHandlerV2.batchCall` reinforces the same "no fault isolation" design at a higher level — a single failing call in the array reverts the entire batch: [4](#0-3) [5](#0-4) 

Because Hyperbridge relayers batch multiple independent requests/responses from potentially different users/applications under a single MMR proof for gas efficiency, an attacker only needs to control (or register) one destination `IApp` that always reverts on `onAccept`. Any relayer that happens to include that attacker's pending request in the same MMR-proved batch as other legitimate users' requests will have its entire transaction revert, burning all gas spent, and the message delivery for the honest users in that batch is stalled (the relayer must detect the poisoned leaf and rebuild a narrower proof/batch, which is not something the on-chain contracts assist with).

### Impact Explanation
This is a Medium severity issue matching the referenced report's class: an unprivileged party (a malicious application/module developer) can force otherwise-valid, unrelated cross-chain messages to fail delivery and force honest relayers to burn gas repeatedly, since the contracts provide no mechanism to isolate a single bad leaf's callback failure from the rest of the batch. Repeated intentional reverts by a hostile `IApp` create a persistent DoS vector against message delivery routes ("a route unable to deliver messages") and against relayer economics (gas wasted on proof verification that must be redone).

### Likelihood Explanation
Likelihood is Medium: `handlePostRequests`/`handleGetResponses` are permissionless — any relayer can submit any combination of leaves it chooses, but batching for efficiency is standard relayer behavior, and any application author can register a destination contract with adversarial revert behavior without needing any privilege. Once even one pending request destined for that malicious `IApp` is included by a relayer in a shared-proof batch with legitimate requests, the failure is deterministic and repeatable.

### Recommendation
Wrap the external dispatch call to `IApp` callbacks (inside `dispatchIncoming`/`dispatchTimeOut` in `EvmHost.sol`) in a gas-limited low-level call with `try/catch` (or explicit `call` + gas stipend), and record a per-leaf failure receipt instead of letting the failure propagate and revert the whole batched transaction. This isolates a single misbehaving module's failure to that leaf only, ensuring merkle proof verification work and delivery of all other leaves in the batch complete successfully, consistent with the report's recommendation to avoid unconditional/uncatchable failure propagation from untrusted sub-operations (`revertWithReason`/graceful handling instead of `nearCallPanic`-style full-batch failure).

### Proof of Concept
1. Attacker deploys a malicious `IApp` contract whose `onAccept` (or `onGetResponse`) callback always `revert()`s (or performs an unbounded loop to exhaust gas).
2. Attacker (or any user) dispatches a POST request destined for the malicious `IApp` from a source chain; Hyperbridge relayers pick it up along with unrelated, legitimate POST requests destined for honest apps, and build a single MMR-proved `PostRequestMessage` batch (`evm/src/core/HandlerV2.sol` lines 187-202) for gas efficiency.
3. Relayer calls `handlePostRequests`; the loop at lines 204-209 reaches the malicious leaf, `host.dispatchIncoming` invokes the malicious `IApp`'s callback, which reverts.
4. Because there is no `try/catch`/gas isolation, the entire transaction reverts: the relayer loses all gas spent verifying the multiproof and processing every other (legitimate) request in the batch, and none of the batched messages — including the honest ones — are delivered in that transaction.

### Citations

**File:** evm/src/core/HandlerV2.sol (L123-135)
```text
    /**
     * @dev Process a batch of encoded handler calls in a single transaction.
     * Uses delegatecall to self so msg.sender is preserved and storage writes
     * happen in this contract's context. Atomic, any failure reverts the entire batch.
     * @param calls - array of ABI-encoded handler function calls
     */
    function batchCall(bytes[] memory calls) external {
        uint256 len = calls.length;
        for (uint256 i = 0; i < len; ++i) {
            (bool success, bytes memory returnData) = address(this).delegatecall(calls[i]);
            if (!success) revert BatchCallFailed(i, returnData);
        }
    }
```

**File:** evm/src/core/HandlerV2.sol (L187-202)
```text
        uint256 requestsLen = request.requests.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](requestsLen);

        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }

        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();
```

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```

**File:** evm/src/core/HandlerV2.sol (L241-246)
```text
        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
```

**File:** sdk/packages/core/contracts/interfaces/IHandlerV2.sol (L32-39)
```text
interface IHandlerV2 {
    /**
     * @dev Process a batch of encoded handler calls in a single transaction.
     * Each element in `calls` is an ABI-encoded call to one of the handler functions.
     * The handler decodes and executes them sequentially. If any call fails, the entire batch reverts.
     * @param calls Array of ABI-encoded function calls
     */
    function batchCall(bytes[] memory calls) external;
```
