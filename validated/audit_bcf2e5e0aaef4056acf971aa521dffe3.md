### Title
Reentrant `onAccept`/`on_accept` callback can steal relayer-fee attribution for other requests in the same batch - ([File: evm/src/core/EvmHost.sol], [File: modules/ismp/core/src/handlers/request.rs])

### Summary
Both the EVM and Substrate ISMP request handlers process a batch of `PostRequest`s sequentially, storing the delivering relayer's identity in a per-request receipt (`_requestReceipts[commitment]` on EVM, `RequestReceipts[commitment]` on Substrate) immediately before invoking the destination module's callback (`onAccept` / `on_accept`). That receipt is later read by the fee-accumulation logic to decide who gets paid the relayer fee for delivering the request. Because the callback is an arbitrary, attacker-controllable contract/pallet invoked mid-loop, it can reenter the request handler with a second, independently-valid message covering a *different, not-yet-processed* request from the same original batch, claiming that request's receipt for itself. When the original relayer's loop reaches that request, the receipt already exists and the entry is rejected as a duplicate (without reverting the whole batch), so the honest relayer loses the fee it expected to earn for delivering that entry while still paying for verification and dispatch of the whole batch. This is the same bug class as the PoolTogether report: a callback invoked as part of a batched claim/dispatch flow reenters the batch-processing function to redirect fees intended for the original caller to itself, with the "loser" entries silently absorbed via the batch's per-item error handling instead of a full revert.

### Finding Description
On the Substrate side, `handle<H>` in `modules/ismp/core/src/handlers/request.rs` verifies membership for the whole batch up front, then iterates the requests and, for each one, stores the request receipt keyed to `msg.signer` immediately before calling `cb.on_accept(request)`: [1](#0-0) 

The code comment explicitly acknowledges that "a prior request's on_accept in this same batch could have stored a receipt for this request (directly or by re-entering the handler)" and only guards against invoking `on_accept` a second time for the same request - it does not prevent a malicious module's `on_accept` from reentering the handler with its own valid proof for a *different* request in the batch, before the original loop reaches it. Errors are collected per-request into a `Vec` rather than aborting the batch: [2](#0-1) 

The stolen `RequestReceipts[commitment]` is exactly what `pallet-relayer`'s `accumulate()` later reads to decide the fee beneficiary: `decode_receipt_relayer` extracts the relayer address from the destination-chain receipt proof, and that address is credited with the fee: [3](#0-2) 

The mirror-image EVM path has the identical unguarded pattern: `EvmHost.dispatchIncoming(PostRequest)` unconditionally sets `_requestReceipts[commitment] = relayer` immediately before making an untrusted external call into the destination contract's `onAccept`, with no reentrancy lock: [4](#0-3) 

On EVM the destination contract for a `PostRequest` is fully permissionless attacker-controlled code, and at least one first-party app (`HyperFungibleToken.onAccept`) already forwards attacker-supplied `message.data` into `ICallDispatcher.dispatch(message.data)` during minting, which is a plausible concrete reentry point into the handler from within a legitimately-triggered callback: [5](#0-4) 

### Impact Explanation
Whoever is recorded as the delivering relayer in `RequestReceipts`/`_requestReceipts` for a given request commitment is the party paid the relayer fee for that delivery once a withdrawal/accumulate proof is later submitted. By reentering the batch handler from an `onAccept`/`on_accept` callback with a valid message covering a not-yet-processed sibling request, an attacker can claim that request's fee attribution for itself at effectively zero incremental delivery cost, while the honest relayer - who paid to verify and submit the entire batch - is rejected with `DuplicateRequest`/an equivalent duplicate error for that entry and loses the associated relayer fee. This is a direct fee-theft vector against Hyperbridge's relayer incentive/reward accounting, reachable from a single permissionless message-delivery submission, matching the accepted scope ("relayer fee and reward accounting").

### Likelihood Explanation
Exploitability requires only that the attacker control (or influence via forwarded calldata, as with `HyperFungibleToken`'s `ICallDispatcher.dispatch`) the destination module targeted by one request in a multi-request batch, and that they hold or can construct a second valid state/membership proof for another request in that same batch to submit reentrantly. Both conditions are attacker-reachable on a permissionless network where destination modules/contracts are arbitrary and batches routinely contain requests to multiple `to` addresses. The code's own comments show the maintainers are aware of the reentrancy path but have only closed the "double-invoke on_accept for the same request" case, not the "steal a sibling request's attribution" case.

### Recommendation
Add reentrancy protection around the entire batch-processing entry point (`handle<H>` on Substrate, `dispatchIncoming`/`handlePostRequests` on EVM) so that a callback invoked mid-batch cannot re-enter the handler at all, rather than only re-checking for duplicate receipts on the specific request being dispatched. Alternatively, snapshot/lock the set of receipts to be written for the whole batch before invoking any callback, and reject (rather than skip) any batch containing a request whose receipt state changed underneath it during processing, so that fee attribution for a batch can only ever be earned by the party that paid to submit and verify it.

### Proof of Concept
1. Relayer R submits a batch `handle(msg)` containing `PostRequest #1` (to attacker-controlled module `M`) and `PostRequest #2` (to victim module `V`), with a valid membership proof for both.
2. The loop reaches request #1 first, stores `RequestReceipts[commitment1] = R`, then calls `M.on_accept(request1)`.
3. Inside `on_accept`, `M` reenters `handle(msg2)` with an independently valid message/proof also covering request #2 (`commitment2`), signed/submitted as attacker `A`. Since `RequestReceipts[commitment2]` does not exist yet, this reentrant call succeeds: `RequestReceipts[commitment2] = A`, and `V.on_accept(request2)` runs.
4. Control returns to the outer loop for request #2: `host.request_receipt(&wrapped_req).is_some()` is now true, so it errors with `DuplicateRequest` for that entry - but per-request errors are collected into a `Vec` rather than reverting the whole batch, so R's overall transaction still succeeds for request #1.
5. When fee accumulation is later run, `RequestReceipts[commitment2]` proves attacker `A` (not relayer `R`) delivered request #2, so `A` collects that portion of the relayer fee even though `R` paid for the whole batch's verification and delivery.

### Citations

**File:** modules/ismp/core/src/handlers/request.rs (L99-126)
```rust
		.map(|request| {
			let wrapped_req = Request::Post(request.clone());
			let mut lambda = || {
				let cb = router.module_for_id(request.to.clone())?;
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
				Ok(res)
```

**File:** modules/ismp/core/src/handlers/request.rs (L129-134)
```rust
			let res = lambda().and_then(|res| res);
			res
		})
		.collect::<Vec<_>>();

	Ok(MessageResult::Request { events: result, weight: total_weights })
```

**File:** modules/pallets/relayer/src/accumulate.rs (L287-298)
```rust
			let encoded_receipt = dest_result
				.get(&dest_key)
				.cloned()
				.flatten()
				.ok_or_else(|| Error::<T>::ProofValidationError)?;
			let address = Self::decode_receipt_relayer(
				proof.dest_proof.height.id.state_id,
				&encoded_receipt,
			)?;
			let entry = result.entry(address).or_insert(U256::zero());
			*entry += fee;
			commitments.push(commitment);
```

**File:** evm/src/core/EvmHost.sol (L794-818)
```text
    function dispatchIncoming(PostRequest memory request, address relayer) external restrict(_hostParams.handler) {
        address destination = _bytesToAddress(request.to);
        uint256 size;
        assembly {
            size := extcodesize(destination)
        }
        if (size == 0) {
            // instead of reverting the entire batch, early return here.
            return;
        }

        // replay protection
        bytes32 commitment = request.hash();
        _requestReceipts[commitment] = relayer;

        (bool success,) = address(destination)
            .call(abi.encodeWithSelector(IApp.onAccept.selector, IncomingPostRequest(request, relayer)));

        if (!success) {
            // so that it can be retried
            delete _requestReceipts[commitment];
            return;
        }
        emit PostRequestHandled({commitment: commitment, relayer: relayer});
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```
