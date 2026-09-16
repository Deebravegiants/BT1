### Title
Atomic batch processing of ISMP messages allows exchange/relay griefing via a single failing message reverting the entire batch — ([File: evm/src/core/HandlerV2.sol], [File: modules/pallets/ismp/src/impls.rs])

### Summary
Hyperbridge's message-delivery path exhibits the same "batch processing griefing" pattern described in the external report. On the EVM side, `HandlerV2.batchCall` executes an array of relayer-supplied handler calls (`handleConsensus`, `handlePostRequests`, `handleGetResponses`, etc.) atomically via `delegatecall`; if **any single call in the batch fails, the entire transaction reverts** [1](#0-0) . On the Substrate side, `pallet_ismp::Pallet::execute` short-circuits on the first invalid message in a `Vec<Message>` and the dispatchable `handle_unsigned` that wraps it is marked `#[frame_support::transactional]`, so the whole extrinsic (and every otherwise-valid message bundled with it) is discarded on a single failure [2](#0-1) [3](#0-2) . There is no "NoThrow"/best-effort batch variant that skips a failing item and continues processing the rest.

### Finding Description
Hyperbridge relayers explicitly batch multiple unrelated cross-chain messages into a single atomic transaction to amortize gas/overhead:

- `submit_batch_messages` in the EVM messaging relayer builds one `IHandlerV2.batchCall(bytes[])` transaction out of N independent `Message`s (consensus updates, POST requests, GET responses) and documents that "if any inner call reverts, the whole transaction reverts" [4](#0-3) .
- `HandlerV2.batchCall` loops over the calls and `delegatecall`s each one to `address(this)`; the first failure aborts the whole batch with `BatchCallFailed` [5](#0-4) .
- Inside `handlePostRequests`, each leaf in the batch is checked for duplication right before dispatch: `if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();` [6](#0-5) . Because `handlePostRequests` itself is one of the delegatecalled entries inside `batchCall`, a single already-delivered (or otherwise invalid/expired) request anywhere in the leaf set aborts delivery of every other valid, unrelated request batched alongside it.
- On the Substrate side, `Pallet::<T>::execute` maps every message in the batch through `handle_incoming_message` and immediately fails the whole call via `.collect::<Result<Vec<_>, _>>()` if any single message errors [7](#0-6) , and `handle_unsigned` — the only permissionless entry point for delivering ISMP messages to a parachain — is `#[frame_support::transactional]`, guaranteeing full-batch rollback on any single message failure [8](#0-7) . `validate_unsigned` re-runs `Self::execute` at the mempool-validation stage too, meaning a batch mixed with even one bad message is rejected outright before inclusion [9](#0-8) .

This is precisely the bug class in the external report: batch processing of independent operations that all revert together if one item is invalid, with no "NoThrow" fallback. Because `handle_unsigned` is permissionless (`ensure_none(origin)`) and `batchCall` is fully permissionless as well, an attacker does not need any special privilege to exploit this — they simply need to observe a relayer's pending batch (mempool/relayer telemetry) and race in a transaction that invalidates one item of that batch (e.g., deliver one of the bundled requests individually first so the batched copy hits `DuplicateMessage()`, or push a request past its timeout right before the batch lands so `MessageTimedOut()`/`RequestTimeoutNotElapsed` fires).

### Impact Explanation
A successful griefing attack:
- Causes complete failure of an entire relayer-submitted batch of otherwise valid ISMP messages (consensus updates, POST requests, GET responses) on EVM destinations, or an entire `handle_unsigned` batch on Substrate destinations, wasting relayer gas/compute and delaying delivery of every unrelated message bundled together.
- Delays cross-chain message delivery for all counterparties whose requests/responses happened to be batched with the targeted message — this can stall token bridge mints, intents settlement, or application state updates that depend on timely message delivery.
- Can be repeated cheaply and asymmetrically (the attacker's single griefing action costs far less than the relayer's rebuilt/resubmitted batch), degrading the reliability of Hyperbridge's core message-delivery guarantees.

This matches "Medium/High" severity for a route being made temporarily unable to deliver messages, without requiring any privileged role.

### Likelihood Explanation
Both `HandlerV2.batchCall` and `handle_unsigned` are explicitly documented as permissionless/relayer-agnostic entry points intended to reduce gas overhead by grouping messages [10](#0-9) . The relayer code paths that produce these batches are visible in the open-source tesseract messaging crate (`build_batch_inner_calls`, `submit_batch_messages`), so an attacker can predict batch composition or observe it in the mempool, and craft a front-running transaction targeting exactly one message in a pending batch to invalidate it. No governance, admin, or validator privileges are required — only the ability to submit an ordinary transaction/extrinsic ahead of the relayer's batch.

### Recommendation
- **Short term:** Implement "NoThrow" batch variants for `HandlerV2.batchCall` (e.g., catch per-call failures with low-level `call`/try-catch semantics and emit a `CallFailed(index, reason)` event rather than reverting the whole batch) and for `pallet_ismp::execute`/`handle_unsigned` (process each `Message` independently, collect individual `Result`s, and only fail/skip the offending message rather than aborting the entire `Vec<Message>`).
- **Long term:** When designing any function that iterates over relayer- or user-supplied batches of independent operations, assume adversarial inputs can be interleaved and design for partial success/partial failure isolation, consistent with the existing no-throw fill patterns elsewhere in the codebase.

### Proof of Concept
1. A relayer builds a batch `[handlePostRequests({leafA, leafB, leafC})]` (or a multi-call `batchCall([handleConsensus(...), handlePostRequests(...)])`) intending to deliver three independent POST requests in one atomic EVM transaction, per `build_batch_inner_calls`/`submit_batch_messages` [11](#0-10) .
2. An attacker observes this pending transaction in the mempool and front-runs it with their own transaction delivering `leafB` alone (a permissionless call to `handlePostRequests`).
3. The relayer's original batch transaction lands after; when it processes `leafB` inside the loop, `host.requestReceipts(leaf.request.hash()) != address(0)` is now true, so it reverts with `DuplicateMessage()` [6](#0-5) .
4. Because this call was itself one delegatecall entry inside `batchCall`, the revert propagates and the entire `batchCall` transaction reverts per `if (!success) revert BatchCallFailed(i, returnData);` [5](#0-4) , causing `leafA` and `leafC` — both still valid and undelivered — to also fail delivery, forcing the relayer to rebuild and resubmit the batch.
5. The analogous PoC on Substrate: submit a `handle_unsigned` extrinsic containing `[MessageA (valid), MessageB (duplicate/expired)]`; `Pallet::execute`'s `.collect::<Result<Vec<_>,_>>()` fails on `MessageB`, and because the call is `#[frame_support::transactional]`, `MessageA`'s otherwise-successful processing is rolled back too [7](#0-6) [8](#0-7) .

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

**File:** evm/src/core/HandlerV2.sol (L204-209)
```text
        for (uint256 i = 0; i < requestsLen; ++i) {
            PostRequestLeaf memory leaf = request.requests[i];
            // duplicate request?
            if (host.requestReceipts(leaf.request.hash()) != address(0)) revert DuplicateMessage();
            host.dispatchIncoming(leaf.request, _msgSender());
        }
```

**File:** modules/pallets/ismp/src/impls.rs (L37-51)
```rust
impl<T: Config> Pallet<T> {
	/// Execute the provided ISMP datagrams, this will short circuit if any messages are invalid.
	/// This also charges fee on valid message delivery
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

**File:** modules/pallets/ismp/src/lib.rs (L358-382)
```rust
	#[pallet::call]
	impl<T: Config> Pallet<T> {
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

**File:** modules/pallets/ismp/src/lib.rs (L614-626)
```rust
		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			use ismp::{
				messaging::{hash_request, ConsensusMessage, FraudProofMessage, RequestMessage},
				router::Request,
			};
			let messages = match call {
				Call::handle_unsigned { messages } => messages,
				_ => Err(TransactionValidityError::Invalid(InvalidTransaction::Call))?,
			};

			let events =
				Self::execute(messages.clone()).map_err(|_| InvalidTransaction::BadProof)?;

```

**File:** tesseract/messaging/evm/src/tx.rs (L441-461)
```rust
/// Submit a full batch of ISMP messages as a single `IHandlerV2.batchCall` transaction.
///
/// One tx replaces what would otherwise be N separate txs (one per message),
/// cutting gas overhead and nonce management complexity. Atomic: if any
/// inner call reverts, the whole transaction reverts.
pub async fn submit_batch_messages(
	client: &EvmClient,
	messages: Vec<Message>,
) -> anyhow::Result<SubmitOutcome> {
	if messages.is_empty() {
		return Ok((BTreeSet::new(), Vec::new(), Vec::new()));
	}

	let handler_addr = Address::from_slice(&client.handler().await?.0);
	let from = Address::from_slice(&client.address);
	let gas_price = fetch_gas_price(client, false).await?;
	let chain_gas_limit = get_chain_gas_limit(client.state_machine);

	let inner_calls = build_batch_inner_calls(client, &messages).await?;
	let handler_v2 = HandlerV2Instance::new(handler_addr, client.signer.clone());
	let call = handler_v2.batchCall(inner_calls);
```

**File:** sdk/packages/core/contracts/interfaces/IHandlerV2.sol (L25-39)
```text
/**
 * @title IHandlerV2
 * @author Polytope Labs (hello@polytope.technology)
 * @notice Extended handler interface that supports batching multiple handler calls into a single transaction.
 * @dev Relayers can ABI-encode individual handler calls (handleConsensus, handlePostRequests, etc.)
 * and submit them as a single batchCall, reducing gas overhead and simplifying relayer logic.
 */
interface IHandlerV2 {
    /**
     * @dev Process a batch of encoded handler calls in a single transaction.
     * Each element in `calls` is an ABI-encoded call to one of the handler functions.
     * The handler decodes and executes them sequentially. If any call fails, the entire batch reverts.
     * @param calls Array of ABI-encoded function calls
     */
    function batchCall(bytes[] memory calls) external;
```
