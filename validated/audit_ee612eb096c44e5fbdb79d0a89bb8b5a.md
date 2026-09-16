### Title
Unbounded batch atomicity in `HandlerV2` and pallet-ismp `execute` lets one poisoned/duplicate message revert or fail an entire batch of otherwise-valid messages - (File: evm/src/core/HandlerV2.sol, modules/pallets/ismp/src/impls.rs)

### Summary
The external report describes a "block packing bug": independent operations (a slashing and a voluntary exit) are packed into the same block without regard to their processing order, so one operation's side effect (consuming the validator) causes the other to fail even though both were individually valid when submitted. The root cause is that batched, independently-submitted items are processed as an all-or-nothing unit despite having no real interdependency requirement.

Hyperbridge has a structurally analogous pattern in its message-batching paths: `HandlerV2.handlePostRequests` / `handleGetResponses` process an array of independent leaves in a single call, and `IHandlerV2.batchCall` composes multiple such handler calls into one atomic transaction; on the Substrate side, `Pallet::execute` (`modules/pallets/ismp/src/impls.rs`) maps `handle_incoming_message` over a `Vec<Message>` and short-circuits the *entire* extrinsic if any single message errors.

### Finding Description
In `HandlerV2.handlePostRequests` (`evm/src/core/HandlerV2.sol:181-210`), a relayer submits a batch of `PostRequestLeaf`s under one merkle proof. After proof verification, a second loop checks each leaf for a duplicate receipt and reverts unconditionally if found: [1](#0-0) 

This revert is not caught or skipped — it aborts the whole `handlePostRequests` call, including all of the other, still-valid leaves bundled with it. The same shape recurs in `handleGetResponses`: [2](#0-1) 

`IHandlerV2.batchCall` compounds this: it documents that "if any call fails, the entire batch reverts" [3](#0-2) 
and the relayer (`tesseract/messaging/evm/src/tx.rs`) actively packs many independent `Message::Request`/`Message::Response`/`Message::Consensus` entries into one `batchCall`, explicitly noting "Atomic: if any inner call reverts, the whole transaction reverts": [4](#0-3) 

By contrast, when an app-level callback (`onAccept`/`on_response`) itself fails, both the EVM and Substrate hosts are careful to *not* propagate that failure to the rest of the batch — `dispatchIncoming`'s failure path deletes the receipt and returns without reverting so the rest of a batch proceeds, per the documented flow: [5](#0-4) 
This shows the codebase already recognizes that per-message isolation is the correct behavior for application-level failures, but the duplicate/receipt check that happens earlier, inside the handler's loop, is not given the same isolation and instead aborts the entire call.

The Substrate side generalizes the same defect at the extrinsic level. `Pallet::execute` maps `handle_incoming_message` over the whole `Vec<Message>` of the unsigned `handle_unsigned` extrinsic and collects with `?`, so a single invalid/duplicate message anywhere in the vector fails the *entire* extrinsic before any events are emitted or any valid message is applied: [6](#0-5) [7](#0-6) 
The same atomic-collect-then-fail pattern appears in the response handler for batched Get responses, where a single `DuplicateResponse` anywhere in `msg.requests` aborts processing of the whole `ResponseMessage`: [8](#0-7) 

### Impact Explanation
`handle_unsigned` is explicitly an unsigned extrinsic "that permits anyone execute ISMP messages for free" (see doc comment at `modules/pallets/ismp/src/lib.rs:360-365`), and relayer proofs/calldata for pending messages are public once broadcast (mempool-visible or reconstructable from public MMR/merkle data). An unprivileged actor can therefore:
- Observe a relayer's pending `handlePostRequests`/`handleGetResponses`/`batchCall` transaction (or Substrate `handle_unsigned` extrinsic) bundling N independent, otherwise-deliverable messages.
- Front-run it by submitting just one of the same leaves/messages individually (paying only its own small gas/weight), causing `DuplicateMessage`/`DuplicateResponse` when the relayer's bundled transaction lands.
- Because the check is unguarded, the entire bundled transaction reverts (EVM) or the entire extrinsic fails (Substrate) — not just the duplicated entry — delaying or repeatedly griefing delivery of the other N-1 unrelated, valid messages.

This matches the "a route unable to deliver messages" impact category explicitly accepted by the validation rules: repeated griefing can stall cross-chain message delivery for a state machine route, degrading availability of the bridge without requiring any privileged access.

### Likelihood Explanation
The attack requires no special privilege — any address can call `handlePostRequests`/`handleGetResponses`/submit `handle_unsigned` for a single message once its proof/commitment is publicly known, and relayer batches are visible in the mempool or can be reconstructed from on-chain/off-chain data the relayer already fetched. The cost to the attacker is small (one cheap duplicate-submission tx) relative to the potential to force expensive relayer batches to fail repeatedly, giving a straightforward and repeatable griefing vector rather than a rare edge case.

### Recommendation
Isolate per-message failures within a batch the same way `dispatchIncoming`'s app-callback failure is already isolated: wrap the duplicate/receipt check (and other per-leaf validation) in `handlePostRequests`/`handleGetResponses` so a single already-processed leaf is skipped (e.g., continue) rather than reverting the whole call, and apply the analogous fix to `Pallet::execute` and `handlers::response::handle` so a single invalid/duplicate `Message`/`Get` request in a batch does not abort processing of the remaining valid ones in the same extrinsic.

### Proof of Concept
1. Relayer builds a `PostRequestMessage` covering leaves `[A, B, C]` (or a Substrate `handle_unsigned([A, B, C])`) and broadcasts it.
2. Attacker observes the pending calldata/extrinsic, extracts leaf `B`, and submits it alone (`handlePostRequests` with just `B`, or `handle_unsigned([B])`) with higher gas/priority so it lands first.
3. `host.requestReceipts(B.hash())` is now non-zero.
4. The relayer's original `[A, B, C]` transaction/extrinsic lands and reverts entirely at `revert DuplicateMessage()` (`evm/src/core/HandlerV2.sol:207`) or fails the whole `handle_unsigned` call via `Pallet::execute`'s `?`-propagation (`modules/pallets/ismp/src/impls.rs:46-51`), even though `A` and `C` were valid, undelivered, and independent of `B`.

### Citations

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

**File:** tesseract/messaging/evm/src/tx.rs (L441-446)
```rust
/// Submit a full batch of ISMP messages as a single `IHandlerV2.batchCall` transaction.
///
/// One tx replaces what would otherwise be N separate txs (one per message),
/// cutting gas overhead and nonce management complexity. Atomic: if any
/// inner call reverts, the whole transaction reverts.
pub async fn submit_batch_messages(
```

**File:** sdk/packages/core/docs/ai/flows/how-a-cross-chain-delivery-reaches-the-gateway-and-where-the.md (L10-13)
```markdown
2. `EvmHost.dispatchIncoming` (restricted to the handler) writes a receipt for the request
   commitment, then low-level calls the module with `IApp.onAccept(IncomingPostRequest(request,
   relayer))`. If that call fails the host deletes the receipt and returns without reverting, so the
   rest of the batch proceeds and the message stays deliverable.
```

**File:** modules/pallets/ismp/src/impls.rs (L40-51)
```rust
	pub fn execute(messages: Vec<Message>) -> Result<Vec<events::Event>, Error<T>> {
		let host = Pallet::<T>::default();

		let message_results = messages
			.iter()
			.map(|msg| handle_incoming_message(&host, msg.clone()))
			.collect::<Result<Vec<_>, _>>()
			.map_err(|err| {
				log::debug!(target: "ismp", "Handling Error {:#?}", err);
				Pallet::<T>::deposit_event(Event::<T>::Errors { errors: vec![err.into()] });
				Error::<T>::InvalidMessage
			})?;
```

**File:** modules/pallets/ismp/src/lib.rs (L360-382)
```rust
		/// Execute the provided batch of ISMP messages, this will short-circuit and revert if any
		/// of the provided messages are invalid. This is an unsigned extrinsic that permits anyone
		/// execute ISMP messages for free, provided they have valid proofs and the messages have
		/// not been previously processed.
		///
		/// The dispatch origin for this call must be an unsigned one.
		///
		/// - `messages`: the messages to handle or process.
		///
		/// Emits different message events based on the Message received if successful.
		#[pallet::weight(weight())]
		#[pallet::call_index(0)]
		#[frame_support::transactional]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/ismp/core/src/handlers/response.rs (L44-68)
```rust
	// Reject duplicate Get requests within the batch.
	dedup_requests::<H>(&msg.requests())?;

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

		let res = GetResponse { get: get.clone(), values: Default::default() };

		if host.response_receipt(&res).is_some() {
			Err(Error::DuplicateResponse { meta: (&res).into() })?
		}
	}
```
