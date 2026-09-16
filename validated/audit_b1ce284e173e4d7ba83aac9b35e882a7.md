I have enough evidence to construct the analog now. Let me confirm the exact `validate_unsigned` re-execution behavior one more time to be precise about the mempool-level cost duplication.### Title
Unbounded, uncharged batch verification in `pallet-ismp::validate_unsigned` enables network-wide Rapid-Reset-style DoS - (File: `modules/pallets/ismp/src/lib.rs`)

### Summary
`pallet-ismp`'s unsigned `handle_unsigned` extrinsic is validated by running the **entire** message-processing pipeline — including expensive cryptographic/state-proof verification for every message in an unbounded `Vec<Message>` — inside `validate_unsigned`, which every full/collator node executes for free on every gossiped transaction, before any fee, weight, or inclusion accounting applies. This mirrors the HTTP/2 Rapid Reset pattern: the "stream" (verification work) is fully performed by the peer and then immediately discarded ("reset") when validation fails or the transaction pool drops it, at zero cost to the sender and with no per-connection/per-peer accounting limiting how many such cycles can be forced.

### Finding Description
`Pallet::execute` runs `handle_incoming_message` over every message in the batch, dispatching to consensus/request/response/timeout handlers that perform BEEFY/SP1/ECDSA signature checks, merkle/MMR proof verification, and state (non-)membership trie proofs: [1](#0-0) 

`handle_unsigned` simply calls `Self::execute(messages.clone())` with no cap on `messages.len()`, and each individual message (e.g. `RequestMessage`, `TimeoutMessage`) itself carries an unbounded inner `Vec` of requests/responses that all get fully proof-checked: [2](#0-1) [3](#0-2) [4](#0-3) 

Critically, `ValidateUnsigned::validate_unsigned` for `pallet-ismp` does not perform a cheap, bounded pre-check before running this full pipeline — it calls the identical `Self::execute(messages.clone())` used for actual dispatch, explicitly noting "empty pre-dispatch so we don't modify storage" (implying `validate_unsigned` itself does the heavy lifting): [5](#0-4) 

Because `Call::handle_unsigned` is `ensure_none` (unsigned, feeless) and validated by every node that receives it over the transaction-pool gossip network before any block inclusion, an attacker can craft a stream of syntactically valid but ultimately-rejected batches (e.g. slightly different consensus proof bytes, expired/garbage state proofs, or huge request batches with bogus merkle proofs) and repeatedly submit them. Each submission forces every reachable validator/collator node to perform full cryptographic verification (secp256k1 recovery, MMR/merkle-multiproof checks, SP1 Groth16 verification) during `validate_unsigned`, and the resulting rejection ("BadProof") discards the work with `longevity: 25` — analogous to a HEADERS immediately followed by RST_STREAM: the server (node) does the expensive setup, then the "stream" (tx) is torn down, and the cycle repeats with no accounting of how much verification work a single unbounded/unauthenticated request can trigger.

The design intent documented elsewhere ("Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing") assumes the validation itself is cheap — but here validation *is* the expensive full-execution path, so the claimed spam mitigation does not actually bound CPU cost; it only bounds *chain storage* cost.

### Impact Explanation
This is a compute-based denial-of-service vector reachable by any unprivileged party able to submit or gossip unsigned extrinsics to `pallet-ismp` nodes (relayers, dispatchers, or any network peer), consistent with the CWE-400 classification of the underlying Rapid Reset report. Sustained submission of large batches/expensive-but-invalid proofs can degrade or halt block production and message delivery capacity across the network — a route rendered unable to reliably deliver messages — without the attacker paying any transaction fee (the call is `ensure_none`/feeless by design), and without any dedicated size/complexity cap on the unsigned batch separate from the full execution path.

### Likelihood Explanation
Medium-High. No signature, stake, or reputation is required to submit unsigned `handle_unsigned` calls — only "valid-looking" proof structures that pass initial decoding are needed to force execution into the expensive verification branches (BEEFY/SP1/ECDSA recovery, MMR/trie proofs). An attacker only needs to vary payload bytes (proof content, nonce, message count) between submissions to avoid the `provides`-tag dedup and repeat the cycle indefinitely, and can do this against many/most full nodes in parallel via p2p gossip.

### Recommendation
Add a cheap, strictly bounded pre-validation stage in `validate_unsigned` (e.g., message count / total request count caps, structural sanity checks, and proof-size limits) that runs **before** any cryptographic verification, so full `execute()`-equivalent work is only performed once a transaction has passed lightweight admission control. Consider also weighting `validate_unsigned` cost against a per-peer/per-source rate limit at the transaction-pool level, and capping `Vec<Message>` / inner request-vector sizes at the type level (`BoundedVec`) instead of `Vec`.

### Proof of Concept
Conceptually:
1. Construct a `pallet_ismp::Call::handle_unsigned` with a large `Vec<Message>` (e.g., hundreds of `RequestMessage`/`TimeoutMessage` entries, each with maximal inner `requests`/`responses` vectors and syntactically valid but bogus merkle/BEEFY/SP1 proof bytes).
2. Submit repeatedly via `submit_and_watch` as an unsigned extrinsic, varying proof bytes/nonce each time to bypass the `provides` dedup tag (as already demonstrated for duplicate-rejection behavior in the existing test at [6](#0-5) 
but instead crafting *distinct* invalid batches instead of identical ones).
3. Observe that each submission causes every receiving node to execute `Self::execute(messages.clone())` in full inside `validate_unsigned` (BEEFY/SP1/merkle verification for every message) before rejecting with `InvalidTransaction::BadProof`, at zero cost to the submitter and with `longevity: 25` discarding the result — reproducible indefinitely without paying fees, analogous to HTTP/2 Rapid Reset's HEADERS+RST_STREAM cycle.

### Citations

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

**File:** modules/pallets/ismp/src/lib.rs (L370-382)
```rust
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

**File:** modules/pallets/ismp/src/lib.rs (L604-626)
```rust
	/// This allows users execute ISMP datagrams for free. Use with caution.
	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T> {
		type Call = Call<T>;

		// empty pre-dispatch do we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}

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

**File:** modules/ismp/core/src/handlers/request.rs (L86-93)
```rust
	// Verify membership proof
	let state = host.state_machine_commitment(msg.proof.height)?;
	let commitments = msg
		.requests
		.iter()
		.map(|post| hash_request::<H>(&Request::Post(post.clone())))
		.collect();
	state_machine.verify_membership(host, commitments, state, &msg.proof)?;
```

**File:** modules/ismp/core/src/handlers/timeout.rs (L84-88)
```rust
			let commitments = requests
				.iter()
				.map(|post| hash_request::<H>(&Request::Post(post.clone())))
				.collect();
			state_machine.verify_non_membership(host, commitments, state, &timeout_proof)?;
```

**File:** parachain/simtests/src/pallet_ismp.rs (L281-309)
```rust
	// 3. next send the requests
	let tx = subxt::dynamic::tx(
		"Ismp",
		"handle_unsigned",
		vec![messages_to_value(vec![Message::Request(RequestMessage {
			requests: vec![post.clone().into()],
			proof: proof.clone(),
			signer: signature.encode(),
		})])],
	);

	// send once
	let progress = client.tx().create_unsigned(&tx)?.submit_and_watch().await?;
	// send twice, txpool should reject it
	{
		let tx = subxt::dynamic::tx(
			"Ismp",
			"handle_unsigned",
			vec![messages_to_value(vec![Message::Request(RequestMessage {
				requests: vec![post.clone().into()],
				proof: proof.clone(),
				signer: signature.encode(),
			})])],
		);
		let error = client.tx().create_unsigned(&tx)?.submit_and_watch().await.unwrap_err();
		let subxt::Error::Rpc(RpcError::ClientError(_err)) = error else {
			panic!("Unexpected error kind: {error:?}")
		};
	};
```
