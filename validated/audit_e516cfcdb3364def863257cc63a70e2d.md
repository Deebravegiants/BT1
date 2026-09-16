Based on the investigation, the strongest analog to CVE-2023-33288's use-after-free pattern (a resource that is used/removed by one path while a stale reference to it survives for another path to act on again) is in `EvmHost.sol`'s GET-request lifecycle, where `_requestCommitments[commitment]` is read and paid out in one completion path but never cleared, unlike the sibling completion path which explicitly clears it for replay protection.

### Title
Stale `_requestCommitments` fee metadata after `dispatchIncoming(GetResponse)` enables double payment via a later GET timeout - (File: evm/src/core/EvmHost.sol)

### Summary
`dispatchIncoming(GetResponse, address)` pays the relayer fee for a GET request out of `_requestCommitments[commitment].fee` but never deletes that mapping entry after paying it out, unlike every sibling "consume-once" state transition in the same contract (`dispatchIncoming(PostRequest,...)`, `dispatchTimeOut(GetRequestTimeout,...)`, `dispatchTimeOut(PostRequestTimeout,...)`), which all delete their replay-protection mapping before or immediately after invoking the external callback.

### Finding Description
`dispatchIncoming(GetResponse memory response, address relayer)` sets replay protection only on `_responseReceipts[commitment]` (line 827) before calling the destination module, and afterward pays the relayer fee straight out of `_requestCommitments[commitment].fee` without ever deleting or zeroing that entry: [1](#0-0) 

Compare this to `dispatchTimeOut(GetRequestTimeout, FeeMetadata, bytes32)`, which explicitly `delete`s `_requestCommitments[commitment]` up front specifically for "replay protection," and only re-stores it if the callback fails: [2](#0-1) 

Because the GET-response success path leaves `_requestCommitments[commitment]` populated with the original `FeeMetadata` (fee amount and sender), that commitment slot is still "alive" from the timeout path's perspective. If a GET request timeout is later (or concurrently, across two relayer-submitted batches) processed for the same commitment via `dispatchTimeOut(GetRequestTimeout,...)`, the contract will pay `meta.fee` again — this time refunding `meta.sender` — for a request whose fee was already paid out to the relayer via `dispatchIncoming(GetResponse,...)`. Nothing in `EvmHost.sol` itself checks `_responseReceipts[commitment]` before allowing the timeout dispatch to proceed, unlike the analogous Substrate `pallet-ismp` handler, which explicitly checks for this exact condition: [3](#0-2) 

The Substrate side's request/response/timeout handlers consistently implement "delete-before-callback, restore-on-failure" guards precisely to prevent a stale commitment/receipt from being reused by a second completion path invoked in the same or a later message batch: [4](#0-3) [5](#0-4) 

`EvmHost.sol`'s GET-response path is the one place in the equivalent EVM state machine that omits this cleanup, leaving a stale reference (`_requestCommitments[commitment]`) that a second code path (`dispatchTimeOut`) can act on as if the request were still pending — the same root-cause shape as the kernel's use-after-free: an object is consumed/finalized on one path while a reference usable by a racing/competing path is left dangling.

I was not able to fully verify within the available searches whether `HandlerV2.sol` (which is `restrict(_hostParams.handler)`-gated as the sole caller of these `dispatchIncoming`/`dispatchTimeOut` functions) independently checks `_responseReceipts` before submitting a GET timeout proof to `EvmHost`, since I ran out of tool iterations before reading that file's relevant functions in full. If `HandlerV2` does perform this check before calling `dispatchTimeOut`, the impact would be contained to defense-in-depth rather than a directly exploitable double-payment; if it does not, this is a directly reachable theft/fee-drain path for any relayer or requester able to get a GET response delivered and a stale non-membership timeout proof accepted for the same commitment.

### Impact Explanation
If reachable, this allows the protocol fee for a single GET request to be paid out twice from the fee-token balance held by `EvmHost` — once to the relayer that delivered the response, and again refunded to the original request sender when a timeout is later processed for the same (already-fulfilled) commitment. This is a direct drain of protocol/fee-token funds, matching the "theft of funds" impact bar.

### Likelihood Explanation
Exploitation requires that a timeout proof for a GET request can still be constructed and accepted by the destination consensus client's `verify_non_membership`-equivalent check after a response has already landed — this is state-dependent and gated by whatever height/timestamp checks `HandlerV2` and the state-machine clients perform, which I could not fully confirm from the available context. This uncertainty is called out explicitly above; the code-level guard that exists on the Substrate side and is missing on the EVM side is confirmed with exact line citations.

### Recommendation
In `dispatchIncoming(GetResponse memory response, address relayer)`, delete `_requestCommitments[commitment]` (mirroring the pattern already used in `dispatchTimeOut`) immediately after successfully paying out the relayer fee, so the commitment cannot be later consumed a second time by `dispatchTimeOut(GetRequestTimeout,...)`. Additionally, add an explicit check in the GET-timeout dispatch path (or upstream in `HandlerV2`) that a `_responseReceipts[commitment]` entry does not already exist before honoring a timeout, mirroring the check already present in `modules/ismp/core/src/handlers/timeout.rs:150-154`.

### Proof of Concept
1. Attacker/user dispatches a GET request via `EvmHost`, paying a fee recorded in `_requestCommitments[commitment]`.
2. A relayer delivers a valid `GetResponse` via `HandlerV2` → `EvmHost.dispatchIncoming(GetResponse,...)`; the destination module's `onGetResponse` succeeds, and the fee is paid to the relayer (`evm/src/core/EvmHost.sol:841-845`) — `_requestCommitments[commitment]` is left populated.
3. Separately (or with a manipulated/valid stale proof), a caller drives `HandlerV2` to call `EvmHost.dispatchTimeOut(GetRequestTimeout, meta, commitment)` for the same `commitment` before/without the `HandlerV2`/consensus layer rejecting it as already-answered.
4. `dispatchTimeOut` pays `meta.fee` a second time to `meta.sender` (`evm/src/core/EvmHost.sol:872-875`), resulting in double payment for a single GET request's fee.

### Citations

**File:** evm/src/core/EvmHost.sol (L824-847)
```text
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

**File:** evm/src/core/EvmHost.sol (L856-877)
```text
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

**File:** modules/ismp/core/src/handlers/timeout.rs (L96-112)
```rust
					// Re-check the commitment right before dispatch. The up-front
					// pass above runs before any callback executes; a prior
					// on_timeout in this same batch could have caused the
					// commitment for this request to be removed (directly or by
					// re-entering the handler), and we must not invoke
					// on_timeout for a request that is no longer pending.
					let commitment = hash_request::<H>(&request);
					if host.request_commitment(commitment).is_err() {
						Err(Error::UnknownRequest { meta: (&post).into() })?
					}
					// Delete commitment to prevent rentrancy attack
					let meta = host.delete_request_commitment(&request)?;
					let mut signer = None;
					// If it was a routed request delete the receipt
					if host.host_state_machine() != post.source {
						signer = host.delete_request_receipt(&request).ok();
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

**File:** modules/ismp/core/src/handlers/request.rs (L103-125)
```rust
				// Re-check the receipt right before dispatch. The up-front pass above
				// runs before any callback executes; a prior request's on_accept in
				// this same batch could have stored a receipt for this request
				// (directly or by re-entering the handler), and we must not invoke
				// on_accept a second time.
				if host.request_receipt(&wrapped_req).is_some() {
					Err(Error::DuplicateRequest { meta: wrapped_req.clone().into() })?
				}
				// Store request receipt to prevent reentrancy attack
				let signer = host.store_request_receipt(&wrapped_req, &msg.signer)?;
				let res = cb.on_accept(request.clone()).map(|weight| {
					total_weights.saturating_accrue(weight);

					let commitment = hash_request::<H>(&wrapped_req);
					Event::PostRequestHandled(RequestResponseHandled {
						commitment,
						relayer: signer,
					})
				});
				// Delete receipt if module callback failed so it can be timed out
				if res.is_err() {
					host.delete_request_receipt(&wrapped_req)?;
				}
```
