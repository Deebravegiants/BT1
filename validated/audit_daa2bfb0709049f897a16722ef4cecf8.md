### Title
Missing destination-chain binding check in `handleGetResponses` allows forged `GetResponse` delivery - ([File: evm/src/core/HandlerV2.sol])

### Summary
`HandlerV2.handleGetResponses` accepts a `GetResponse` as valid for a request whenever `host.requestCommitments(hash)` shows *any* known commitment for that request hash, but it never checks that the state machine whose overlay root is being proven (`message.proof.height.id.stateMachineId`) is actually the destination the original `GetRequest` was addressed to. This is structurally the same flaw as CVE-2021-43820: a cache/mapping lookup validates "does this key exist" but omits the binding check that the key is associated with *this particular* resource (there: library ID; here: destination state machine).

### Finding Description
In `evm/src/core/HandlerV2.sol`, `handleGetResponses` verifies incoming `GetResponse`s like this: [1](#0-0) 

The relevant check is: [2](#0-1) 

The comment claims `host.requestCommitments(...)` "also serves as source check," but `requestCommitments` is a flat, global mapping keyed only by the request hash: [3](#0-2) 

It records that *some* `GetRequest` with this hash was dispatched by this host, to *some* destination — not that the destination equals the state machine whose root is being verified in `message.proof.height`. Nothing in the loop compares `leaf.response.request.dest` to `message.proof.height.id.stateMachineId` before the leaf is folded into the MMR proof and, on success, dispatched via `host.dispatchIncoming(leaf.response, _msgSender())`.

This is a real omission, not a stylistic one: the equivalent Substrate/pallet-ismp handler for the same message type explicitly performs this exact binding check before accepting a `GetResponse`: [4](#0-3) 

Line 54 there (`if req.dest_chain() != proof.height.id.state_id { Err(...) }`) is precisely the check missing from the EVM `HandlerV2.handleGetResponses`. The Solidity `handlePostRequests` path also demonstrates the pattern is known and used elsewhere in the same contract (checking `leaf.request.dest.equals(host.host())` before trusting a leaf): [5](#0-4) 

but no analogous dest-vs-proof-height equality check exists for `handleGetResponses`.

### Impact Explanation
Any state machine that Hyperbridge has onboarded a consensus client for (an EVM host, an L2, etc.) produces state/overlay roots that `HandlerV2` will accept once submitted with a valid MMR/state proof rooted at that chain's `stateMachineCommitment`. Because `handleGetResponses` only checks global existence of the request commitment and never checks that the proof's `stateMachineId` equals the `GetRequest.dest` originally targeted, a party that controls (or has compromised) the sequencer/validator set of *any* onboarded state machine can:

1. Observe a `GetRequest` (publicly emitted/dispatched) whose declared `dest` is a *different* chain (e.g., an oracle/price query meant for chain X).
2. Include a fabricated leaf for that same request hash, with attacker-chosen `values`, in their own chain's MMR/state root (chain Y, which they control).
3. Submit `handleGetResponses` with `message.proof.height.id.stateMachineId = Y`. The `requestCommitments` check passes because the request commitment genuinely exists (it was dispatched to X, but the mapping is not scoped by destination). The MMR proof verifies correctly against chain Y's root, since the attacker legitimately controls chain Y's state.
4. `host.dispatchIncoming` invokes the requesting module's response callback with attacker-controlled `values`, causing forged message delivery / unauthorized app action (e.g., an intents/price-oracle consumer application acting on fabricated cross-chain data).

This maps to the required impact categories: forged message delivery and unsound state commitment consumption by application modules that rely on `GetResponse` values (e.g., intents solvers, token-bridge oracle reads reachable through `HandlerV2`, which is directly callable by any relayer).

### Likelihood Explanation
Reachability is high: `handleGetResponses` is a fully permissionless, unprivileged entry point that any relayer can call with a self-supplied proof and `GetResponseMessage`. The only precondition is that the attacker controls (or has compromised) at least one state machine that Hyperbridge already trusts as a consensus source — a bar that varies with which chains are onboarded but is not "malicious governance/admin of Hyperbridge itself," and GetRequest hashes/metadata are public on-chain, so finding a target commitment (analogous to the CVE's "library ID") is not the significant barrier the CVE describes it as for Seafile.

### Recommendation
Add an explicit check in `handleGetResponses` (mirroring `modules/ismp/core/src/handlers/response.rs:54` and the existing pattern in `handlePostRequests`) that `leaf.response.request.dest` equals `message.proof.height.id.stateMachineId` before treating the request commitment as valid for that proof, e.g.:
```solidity
if (!leaf.response.request.dest.equals(<stateMachineId-of proof.height>)) revert InvalidMessageDestination();
```
This binds the cached/mapped request commitment to the specific state machine that the proof authenticates, closing the gap.

### Proof of Concept
Conceptual PoC (cannot be executed without deployment/test harness access, but the code path is deterministic):
1. Chain X and chain Y are both onboarded to `EvmHost` with valid consensus clients.
2. A user's app dispatches `GetRequest{ dest: X, ... }`; `EvmHost` records `_requestCommitments[hash(req)] = FeeMetadata{ sender: user, ... }` (see `evm/src/core/EvmHost.sol:528-534`).
3. Attacker, who controls chain Y's sequencer/state root submission, crafts `GetResponse{ get: req, values: attackerValues }` and includes `leaf.response.hash()` in chain Y's overlay MMR tree at some height `h`.
4. Attacker calls `HandlerV2.handleGetResponses(host, GetResponseMessage{ proof: { height: { stateMachineId: Y, height: h }, ...}, responses: [ { index, response: { get: req, values: attackerValues } } ] })`.
5. `host.requestCommitments(hash(req)).sender != address(0)` → passes (commitment exists, was for X).
6. MMR proof verifies against chain Y's legitimately stored overlay root → passes.
7. `host.dispatchIncoming(response, relayer)` delivers `attackerValues` to the requesting module, which believes it received a legitimate response from chain X.

### Citations

**File:** evm/src/core/HandlerV2.sol (L190-197)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // check destination
            if (!leaf.request.dest.equals(host.host())) revert InvalidMessageDestination();
            // check time-out
            if (timestamp >= leaf.request.timeout()) revert MessageTimedOut();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.request.hash());
        }
```

**File:** evm/src/core/HandlerV2.sol (L217-247)
```text
    function handleGetResponses(IHost host, GetResponseMessage calldata message) external notFrozen(host) {
        uint256 timestamp = block.timestamp;
        uint256 delay = timestamp - host.stateMachineCommitmentUpdateTime(message.proof.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        uint256 responsesLength = message.responses.length;
        MerkleMountainRange.Leaf[] memory leaves = new MerkleMountainRange.Leaf[](responsesLength);

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // don't check for timeouts because it's checked on Hyperbridge

            // known request? also serves as source check
            FeeMetadata memory meta = host.requestCommitments(leaf.response.request.hash());
            if (meta.sender == address(0)) revert UnknownMessage();
            leaves[i] = MerkleMountainRange.Leaf(leaf.index, leaf.response.hash());
        }

        bytes32 root = host.stateMachineCommitment(message.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, message.proof.multiproof, leaves, message.proof.leafCount);
        if (!valid) revert InvalidProof();

        for (uint256 i = 0; i < responsesLength; ++i) {
            GetResponseLeaf memory leaf = message.responses[i];
            // duplicate response?
            if (host.responseReceipts(leaf.response.request.hash()).relayer != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.response, _msgSender());
        }
    }
```

**File:** evm/src/core/EvmHost.sol (L528-534)
```text
    /**
     * @param commitment - commitment to the request
     * @return existence status of an outgoing request commitment
     */
    function requestCommitments(bytes32 commitment) external view returns (FeeMetadata memory) {
        return _requestCommitments[commitment];
    }
```

**File:** modules/ismp/core/src/handlers/response.rs (L47-61)
```rust
	for get in &msg.requests {
		let req = Request::Get(get.clone());

		if req.timed_out(host.timestamp()) {
			Err(Error::RequestTimeout { meta: (&req).into() })?
		}

		if req.dest_chain() != proof.height.id.state_id {
			Err(Error::RequestProofMetadataNotValid { meta: (&req).into() })?
		}

		let commitment = hash_request::<H>(&req);
		if host.request_commitment(commitment).is_err() {
			Err(Error::UnknownRequest { meta: (&req).into() })?
		}
```
