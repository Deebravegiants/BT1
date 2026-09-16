### Title
GET request timeout can be dispatched from a stale historical non‑membership proof after the response was already delivered, causing double `onGetResponse`/`onGetTimeout` execution on EVM hosts - (File: evm/src/core/HandlerV2.sol / evm/src/core/EvmHost.sol)

### Summary
On the EVM side of Hyperbridge, a GET request's timeout can still be dispatched to the destination module *after* its response has already been delivered and executed, because (1) `EvmHost.dispatchIncoming(GetResponse,...)` never clears `_requestCommitments[commitment]` when a response succeeds, and (2) `HandlerV2.handleGetRequestTimeouts` only checks a non‑membership proof against a permanently‑retained *historical* state commitment (`stateMachineCommitment(message.height)`), not the current state. A relayer can submit a timeout using an old height's proof (captured before the response existed) even though the response has since been delivered at a later height. This is the same class of bug as the Rio report: an item that has already been settled via one path (`onGetResponse`) can still be settled a second time via a different path (`onGetTimeout`), because the "already settled" flag isn't checked against the live state before the second settlement executes.

### Finding Description
`EvmHost.dispatchIncoming(GetResponse memory response, ...)` marks the response as received in `_responseReceipts[commitment]` and, on success, pays the relayer fee out of `_requestCommitments[commitment].fee` — but it never deletes `_requestCommitments[commitment]`: [1](#0-0) 

Compare this with `dispatchTimeOut` for GET requests, which unconditionally proceeds as long as `_requestCommitments[commitment]` still exists, with **no check** against `_responseReceipts[commitment]`: [2](#0-1) 

The only guard against timing out an already-answered GET request lives in `HandlerV2.handleGetRequestTimeouts`, which verifies a **non-membership proof of the response receipt on the destination chain's state trie at `message.height`**: [3](#0-2) 

`message.height` maps to `host.stateMachineCommitment(message.height)`, and `EvmHost` never deletes historical state commitments once stored — every height's commitment is retained forever (`_stateCommitments[stateMachineId][height]` is written once in `storeStateMachineCommitment`/`setConsensusState` and never cleared). This means a relayer can hold a **stale proof from an earlier height H**, generated before the destination ever processed/recorded the response, and submit it to `handleGetRequestTimeouts` at any later time — the proof is still valid against the immutable historical commitment for height H, even though the response has since been recorded at a later height H' and already delivered to the source chain via `handleGetResponses` → `dispatchIncoming(GetResponse,...)`.

Sequence:
1. User/app dispatches a GET request; `_requestCommitments[commitment]` is stored with fee metadata.
2. A relayer generates (or a malicious actor withholds) a non-membership proof of the response at an early height H (response not yet produced).
3. Before that timeout is submitted, the response is actually produced, relayed, and delivered via `handleGetResponses`/`dispatchIncoming(GetResponse,...)`: `onGetResponse` executes on the destination app, and the relayer is paid the fee. `_requestCommitments[commitment]` is left intact (not deleted).
4. The relayer (or anyone holding the stale height-H proof) now submits `handleGetRequestTimeouts` using the height-H non-membership proof. Since `state.stateRoot` for height H is still stored, `PolkadotTrie.VerifyProof` succeeds trivially (no response existed yet at H), and `meta.sender != address(0)` still holds because `_requestCommitments[commitment]` was never cleared by the successful response.
5. `EvmHost.dispatchTimeOut(GetRequestTimeout,...)` executes, invoking `onGetTimeout` on the same application that already received `onGetResponse` for the same commitment — a double, contradictory settlement of the same GET request.

This mirrors the Rio report's core issue precisely: a state that was already advanced through one settlement path (`onGetResponse`/response delivery) is allowed to be advanced again through the alternate path (`onGetTimeout`/timeout dispatch), because the "already settled" check is performed against a stale/insufficient state rather than the current one, and no local flag prevents the second path once the first has succeeded. Notably, the equivalent Substrate pallet-ismp implementation explicitly guards against exactly this race with a live check: [4](#0-3) [5](#0-4) 
but the EVM `EvmHost`/`HandlerV2` implementation has no analogous local, current-state check — it only relies on a proof against an immutable historical commitment.

### Impact Explanation
Any Hyperbridge application that dispatches GET requests through `EvmHost`/`HandlerV2` (e.g., the Intent Gateway's source-side cancellation flow, which dispatches a GET to verify an order wasn't filled on the destination before refunding escrow) can have both `onGetResponse` and `onGetTimeout` invoked for the same commitment. Depending on the app's logic, this can lead to: double execution of state transitions gated on "exactly-once" GET resolution (e.g., a refund triggered by `onGetResponse` and a second, conflicting action triggered by `onGetTimeout`), inconsistent internal application state, or funds becoming permanently stuck/duplicated when the two callbacks apply contradictory effects (e.g., one path releases escrow to a solver while the other refunds it to the user). This is a High severity issue: it breaks the fundamental "exactly one terminal callback per request" invariant of the ISMP GET request lifecycle at the EvmHost/HandlerV2 layer, directly reachable by any relayer submitting a normal (permissionless) timeout message with an old but still-valid historical proof.

### Likelihood Explanation
Likelihood is moderate-to-high: no privileged role is required — any relayer (or anyone who can construct/replay a valid Merkle/trie proof against a historical, permanently-retained state commitment) can submit `handleGetRequestTimeouts` at any time after the request's timeout window elapses, regardless of whether the response has since been delivered. The race window exists naturally whenever a response is delivered close to (or after) a request's timeout, which is common when relayers pursue both the response and timeout paths concurrently for fee-maximization, or when a response is delayed and a timeout proof was pre-fetched.

### Recommendation
- In `EvmHost.dispatchIncoming(GetResponse memory response, ...)`, delete `_requestCommitments[commitment]` (or otherwise mark the request as resolved) once the response is successfully processed, mirroring the replay-protection pattern already used for POST requests/timeouts.
- In `HandlerV2.handleGetRequestTimeouts` / `EvmHost.dispatchTimeOut(GetRequestTimeout,...)`, add an explicit local check that `_responseReceipts[commitment]` is empty before proceeding, independent of the (potentially stale) non-membership proof height — analogous to the `GetResponseAlreadyReceived` guard already implemented in `modules/ismp/core/src/handlers/timeout.rs`.
- Alternatively/additionally, require that the non-membership proof height supplied to `handleGetRequestTimeouts` be at or after the latest known state-machine height at submission time, so historical, pre-response proofs cannot be replayed once a response has since landed.

### Proof of Concept
Conceptual PoC (no repo test harness was available to execute in this environment, but the flow follows directly from the cited code):
1. Dispatch a `GetRequest` via `EvmHost.dispatch(DispatchGet)`; note `commitment` and `_requestCommitments[commitment]` populated.
2. Have a relayer collect a non-membership proof of the response at destination height `H` (before the destination has produced a response), but do not submit it yet.
3. Let the actual GET response be produced and delivered normally via `handleGetResponses` → `EvmHost.dispatchIncoming(GetResponse,...)`; confirm `onGetResponse` executes successfully and the relayer is paid, while `_requestCommitments[commitment]` remains non-zero (per [6](#0-5) ).
4. Submit `HandlerV2.handleGetRequestTimeouts` using the height-`H` proof collected in step 2. The non-membership check against `state.stateRoot` for height `H` (per [3](#0-2) ) succeeds because no response existed yet at height `H`, and `meta.sender != address(0)` still holds since `_requestCommitments[commitment]` was never cleared.
5. Observe `onGetTimeout` is invoked on the destination module for a `commitment` that already received `onGetResponse`, confirming the double-settlement.

### Citations

**File:** evm/src/core/EvmHost.sol (L820-847)
```text
    /**
     * @dev Dispatch an incoming GET response to source module
     * @param response - get response
     */
    function dispatchIncoming(GetResponse memory response, address relayer) external restrict(_hostParams.handler) {
        // replay protection
        bytes32 commitment = response.request.hash();
        _responseReceipts[commitment] = ResponseReceipt({
            relayer: relayer,
            responseCommitment: response.hash()
        });

        (bool success,) = _bytesToAddress(response.request.from)
            .call(abi.encodeWithSelector(IApp.onGetResponse.selector, IncomingGetResponse(response, relayer)));

        if (!success) {
            // so that it can be retried
            delete _responseReceipts[commitment];
            return;
        }

        // reward the relayer fee
        uint256 fee = _requestCommitments[commitment].fee;
        if (fee != 0) {
            IERC20(feeToken()).safeTransfer(relayer, fee);
        }
        emit GetRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** evm/src/core/EvmHost.sol (L849-877)
```text
    /**
     * @dev Dispatch an incoming GET timeout to the source module.
     * @notice Does not refund any protocol fees.
     * @param timeout - timed-out get request bundled with the relayer that submitted the timeout proof
     * @param meta - fee metadata for the original request
     * @param commitment - request commitment
     */
    function dispatchTimeOut(
        GetRequestTimeout memory timeout,
        FeeMetadata memory meta,
        bytes32 commitment
    ) external restrict(_hostParams.handler) {
        // replay protection
        delete _requestCommitments[commitment];
        (bool success,) = _bytesToAddress(timeout.request.from)
            .call(abi.encodeWithSelector(IApp.onGetTimeout.selector, timeout));

        if (!success) {
            // so that it can be retried
            _requestCommitments[commitment] = meta;
            return;
        }

        if (meta.fee != 0) {
            // refund relayer fee
            IERC20(feeToken()).safeTransfer(meta.sender, meta.fee);
        }
        emit GetRequestTimeoutHandled({commitment: commitment, dest: string(timeout.request.dest)});
    }
```

**File:** evm/src/core/HandlerV2.sol (L293-321)
```text
    function handleGetRequestTimeouts(IHost host, GetTimeoutMessage calldata message) external notFrozen(host) {
        uint256 delay = block.timestamp - host.stateMachineCommitmentUpdateTime(message.height);
        uint256 challengePeriod = host.challengePeriod();
        if (challengePeriod != 0 && challengePeriod > delay) revert ChallengePeriodNotElapsed();

        // fetch the state commitment
        StateCommitment memory state = host.stateMachineCommitment(message.height);
        if (state.stateRoot == bytes32(0)) revert StateCommitmentNotFound();
        uint256 timeoutsLength = message.timeouts.length;

        for (uint256 i = 0; i < timeoutsLength; ++i) {
            GetRequest memory request = message.timeouts[i];
            // timed-out?
            if (request.timeout() > state.timestamp) revert MessageNotTimedOut();

            bytes32 commitment = request.hash();
            FeeMetadata memory meta = host.requestCommitments(commitment);
            if (meta.sender == address(0)) revert UnknownMessage();

            bytes[] memory keys = new bytes[](1);
            keys[0] = bytes.concat(RESPONSE_RECEIPTS_STORAGE_PREFIX, commitment);

            // verify state trie non-membership proofs
            PolkadotTrie.StorageValue memory entry = PolkadotTrie.VerifyProof(state.stateRoot, message.proof, keys)[0];
            if (entry.value.length != 0) revert InvalidProof();

            host.dispatchTimeOut(GetRequestTimeout(request, _msgSender()), meta, commitment);
        }
    }
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L150-154)
```rust
				// Reject the timeout if a response has already been received for this request
				let response = GetResponse { get: get.clone(), values: Default::default() };
				if host.response_receipt(&response).is_some() {
					Err(Error::GetResponseAlreadyReceived { meta: get.into() })?
				}
```

**File:** modules/ismp/testsuite/src/lib.rs (L354-375)
```rust
/// Reject a GET timeout when the request has already received a response. The request's timeout
/// hasn't elapsed either, so without the response-receipt guard the handler would have failed
/// with `RequestTimeoutNotElapsed` — proving the response check runs first.
pub fn get_response_already_received_check<H>(host: &H) -> Result<(), &'static str>
where
	H: IsmpHost + IsmpDispatcher,
	H::Account: From<[u8; 32]>,
	H::Balance: From<u32> + Default,
{
	let intermediate_state = setup_mock_client(host);
	let get =
		dispatch_get_request(host, &intermediate_state, host.timestamp().as_secs() + 1_000_000);

	let response = GetResponse { get: get.clone(), values: Default::default() };
	host.store_response_receipt(&response, &vec![0u8; 32]).unwrap();

	let timeout_message = Message::Timeout(TimeoutMessage::Get { requests: vec![get] });

	let res = handle_incoming_message(host, timeout_message).map_err(|e| e.downcast().unwrap());
	assert!(matches!(res, Err(Error::GetResponseAlreadyReceived { .. })));
	Ok(())
}
```
