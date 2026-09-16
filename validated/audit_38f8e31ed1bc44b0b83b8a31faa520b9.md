This confirms the critical detail: `pallet-state-coprocessor`'s `validate_unsigned` for `handle_unsigned` calls `Self::handle_get_requests(message.clone())` — the **exact same expensive verification path** — directly during **transaction-pool validation**, i.e., before the extrinsic is even included in a block. Since the doc explicitly states "Pallet ISMP uses unsigned transactions... executed for free," and `handle_unsigned` for the state-coprocessor's `GetRequestsWithProof` runs full membership-proof and state-proof (`verify_membership`, `verify_state_proof`) verification *before* the cheap bandwidth-gate check inside `handle_get_requests` (`modules/pallets/state-coprocessor/src/impls.rs:112-151`), an attacker with a **valid state/consensus proof** but targeting an app/state-machine pair with **no bandwidth allowance** can force every node in the network to redo this expensive cryptographic verification on every gossip/pool-validation pass, for free, repeatedly — because the failure (`GateError::NoAllowance`/`Insufficient`) only surfaces at the very end of the function, after the costly work is done. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Bandwidth gate underprices/undercharges GET-request resource cost, allowing free-of-charge exhaustion of validator resources via `handle_unsigned` - (File: modules/pallets/state-coprocessor/src/impls.rs)

### Summary
Similar to the MemoryGrow underpricing bug (where the cost of an opcode is deferred to a separate pricer that doesn't apply for a given program shape, leaving the opcode priced far below its real cost), Hyperbridge's per-message cost for GET requests is deferred entirely to `pallet-bandwidth`'s gate, which is only consulted *after* the expensive cryptographic work (consensus/state-machine validation and Merkle state-proof verification) has already been performed in `handle_get_requests`. Because `handle_unsigned` for `GetRequestsWithProof` is a fee-less unsigned extrinsic whose entire body — including this expensive verification — is re-executed inside `validate_unsigned` (the transaction-pool admission check), an attacker can submit arbitrarily many valid-proof `GetRequestsWithProof` batches targeting apps/state-machines with no bandwidth allowance, forcing every validating node to pay the full CPU cost of proof verification for zero cost, only to have the bandwidth-gate check reject the message at the very end.

### Finding Description
`pallet-ismp`'s documentation states plainly that unsigned messages are "executed for free," relying on transaction-pool validity checks (valid proofs) to prevent spam [3](#0-2) . For GET requests, the actual resource metering (bandwidth) — the mechanism meant to make dispatch economically sound — is not enforced up front. Instead, `handle_get_requests` performs, in order:
1. Duplicate/timeout/metadata checks.
2. `validate_state_machine` + `verify_membership` for the *source* proof (expensive Merkle verification across all requests in the batch).
3. `validate_state_machine` + per-request `verify_state_proof` for the *destination* state values (more expensive Merkle verification).
4. Only after all of that, per response, `BandwidthGate::try_consume` is called — and if it fails (`NoAllowance`/`Insufficient`), the whole call errors out. [1](#0-0) 

Crucially, this same function is invoked directly inside `ValidateUnsigned::validate_unsigned` for `pallet-state-coprocessor::handle_unsigned`, meaning it runs on every node during mempool gossip/validation, not just once per block: [4](#0-3) 

The bandwidth model documentation itself acknowledges "There's no per-message fee path on dispatch — the cost was paid at purchase time," and that the gate is meant to reject before any real work happens [5](#0-4) , but the code doesn't reorder the check to occur first — exactly analogous to MemoryGrow's cost being "handled by a different part of the code" that, for a class of inputs, never actually applies before the real work is done.

### Impact Explanation
Any unprivileged party can craft a `GetRequestsWithProof` referencing a real, previously-established consensus state and a genuine (or replayed/adjacent) state/response proof for a `(source, app)` pair that has no bandwidth allowance (the overwhelming majority of `(chain, app)` pairs, since bandwidth is opt-in and per-app). Submitting this repeatedly as unsigned transactions forces every full node on the network to perform full Merkle-proof verification (potentially over many keys/values) for free during transaction-pool validation, before the bandwidth check aborts it. This is a network-wide computational resource-exhaustion vector reachable from a single relayed/dispatched extrinsic — the same bug class as the MemoryGrow report (cost deferred to a mechanism that fails to price the real, already-incurred computational work), leading to potential denial of service against Hyperbridge validators/collators.

### Likelihood Explanation
Likelihood is high: the attack requires no privileged role, no governance action, and no cooperation from any other party — only a syntactically valid `GetRequestsWithProof` with a real consensus/state proof (which is cheap to obtain by observing any legitimate cross-chain GET traffic and replaying/adapting it against an unfunded app), and submission is free (unsigned, no transaction fee). The check ordering bug is a straightforward logic issue independent of any external conditions.

### Recommendation
- **Short term:** Move the `BandwidthGate::try_consume` check (or an equivalent conservative upper-bound byte estimate) to the very start of `handle_get_requests`/`validate_unsigned`, before any consensus or state-proof verification is performed, so unfunded apps are rejected cheaply.
- **Long term:** Audit all unsigned/free-of-fee ISMP entry points (`handle_unsigned` for both `pallet-ismp` and `pallet-state-coprocessor`) to ensure any deferred/metered cost model is checked prior to, not after, expensive cryptographic verification; consider weight-metering `validate_unsigned` paths independent of actual dispatch weight so pool validation itself cannot be abused as a free compute sink.

### Proof of Concept
1. Observe (or construct) a valid `Proof` pair (source membership proof + destination state proof) for an existing, verifiable consensus state on Hyperbridge — e.g., by reusing/adjusting the proof structure from a legitimate GET flow such as in `evm/tests/rust/src/tests/get_response.rs`.
2. Build a `GetRequestsWithProof` whose `requests[].from`/`source` corresponds to an app/chain pair with **no bandwidth subscription** and is **not** on the `Allowlist`.
3. Submit `pallet_state_coprocessor::Call::handle_unsigned(message)` as an unsigned transaction repeatedly.
4. Each submission causes `validate_unsigned` to run `handle_get_requests`, which performs full `verify_membership`/`verify_state_proof` work, then fails at `BandwidthGate::try_consume` with `GateError::NoAllowance` — at zero cost to the attacker, but non-trivial CPU cost to every node validating the transaction pool entry. [6](#0-5) [7](#0-6)

### Citations

**File:** modules/pallets/state-coprocessor/src/impls.rs (L62-151)
```rust
	pub fn handle_get_requests(
		GetRequestsWithProof { requests, source, response, address }: GetRequestsWithProof,
	) -> Result<(), Error> {
		// 1. Verify source proofs
		// 2. Extract fees
		// 3. Verify response proof
		// 4. insert GetResponse into mmr and request receipts
		// 5. emit Response events
		let host = <<T as Config>::IsmpHost>::default();

		// Reject duplicate requests within the batch.
		let wrapped: Vec<Request> = requests.iter().cloned().map(Request::Get).collect();
		dedup_requests::<<T as Config>::IsmpHost>(&wrapped)?;

		for req in requests.iter() {
			let full = Request::Get(req.clone());

			// Get requests time out are relative to Hyperbridge
			if full.timed_out(host.timestamp()) {
				Err(Error::RequestTimeout { meta: full.clone().into() })?
			}

			// Source of the request must match the proof
			if full.source_chain() != source.height.id.state_id {
				Err(Error::RequestProofMetadataNotValid { meta: full.clone().into() })?
			}

			// Proof must come from the requested chain
			if full.dest_chain() != response.height.id.state_id {
				Err(Error::RequestProofMetadataNotValid { meta: full.clone().into() })?
			}

			// This request has already been responded to. Mirror `handlers/response.rs:61`:
			// dedup against `response_receipt`, which the dispatch path writes for this exact
			// GetRequest hash after producing a response. The receipt also binds the response
			// commitment, so external auditors can attest "Hyperbridge produced response X for
			// request Y" from one map.
			let probe = GetResponse { get: req.clone(), values: Default::default() };
			if host.response_receipt(&probe).is_some() {
				Err(Error::DuplicateResponse { meta: (&probe).into() })?
			}
		}

		// Ensure the proof height is equal to each retrieval height specified in the Get
		// requests
		if !requests.iter().all(|get| get.height == response.height.height) {
			Err(Error::InsufficientProofHeight)?
		}

		// Verify source proof
		let source_state_machine = validate_state_machine(&host, source.height)?;
		let state_root = host.state_machine_commitment(source.height)?;

		// Verify membership proof to ensure that requests where committed on source chain
		let commitments = requests
			.iter()
			.map(|get| hash_request::<<T as Config>::IsmpHost>(&Request::Get(get.clone())))
			.collect();
		source_state_machine.verify_membership(&host, commitments, state_root, &source)?;

		// Verify response proof
		let dest_state_machine = validate_state_machine(&host, response.height)?;
		let state_root = host.state_machine_commitment(response.height)?;

		// Insert GetResponses into mmr
		let mut responses = vec![];
		// Total payload bytes across this batch, used to mint reputation to
		// the relayer named in `address`. Each response contributes its
		// abi-encoded size — the same quantity the bandwidth gate charges —
		// so the mint stays proportional to the work paid for.
		let mut total_bytes: u32 = 0;
		for req in requests {
			let values: Vec<StorageValue> = dest_state_machine
				.verify_state_proof(&host, req.keys.clone(), state_root.state_root, &response)?
				.into_iter()
				.map(|(key, value)| StorageValue { key, value })
				.collect();

			let response = GetResponse { get: req, values };

			// Meter the app's bandwidth using the full size of the
			// abi-encoded GetResponse. Charged after proof verification
			// so the value sizes are final.
			let bytes = ismp::abi::encode_get_response(&response).len() as u32;
			<T as Config>::BandwidthGate::try_consume(
				&response.get.source,
				&response.get.from,
				bytes,
			)
			.map_err(|err| Error::Custom(alloc::format!("bandwidth gate: {err}")))?;
```

**File:** modules/pallets/state-coprocessor/src/lib.rs (L90-148)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(<T as frame_system::Config>::DbWeight::get().reads_writes(1, 2))]
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			message: GetRequestsWithProof,
		) -> DispatchResult {
			ensure_none(origin)?;

			Self::handle_get_requests(message).map_err(|err| {
				log::error!(target: "ismp", "pallet-coprocessor: {:?}", err);
				Error::<T>::HandlingError
			})?;

			Ok(())
		}
	}

	#[pallet::validate_unsigned]
	impl<T: Config> ValidateUnsigned for Pallet<T>
	where
		T::AccountId: AsRef<[u8]>,
		<T as frame_system::Config>::AccountId: From<[u8; 32]>,
		<T as pallet_ismp::Config>::Balance: Into<u128>,
	{
		type Call = Call<T>;

		// empty pre-dispatch so we don't modify storage
		fn pre_dispatch(_call: &Self::Call) -> Result<(), TransactionValidityError> {
			Ok(())
		}

		fn validate_unsigned(_source: TransactionSource, call: &Self::Call) -> TransactionValidity {
			let Call::handle_unsigned { message } = call else {
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			};

			if let Err(err) = Self::handle_get_requests(message.clone()) {
				log::error!(target: "ismp", "{:?}", err);
				return Err(TransactionValidityError::Invalid(InvalidTransaction::Call));
			}

			let mut messages = message
				.requests
				.iter()
				.map(|get| hash_request::<<T as Config>::IsmpHost>(&Request::Get(get.clone())))
				.collect::<Vec<_>>();
			messages.sort();

			// this is so we can reject duplicate batches at the mempool level
			let msg_hash = sp_io::hashing::keccak_256(&messages.encode()).to_vec();

			Ok(ValidTransaction {
				priority: 100,
				requires: vec![],
				provides: vec![msg_hash],
				longevity: 25,
				propagate: true,
			})
		}
```

**File:** docs/content/developers/polkadot/pallet-ismp/overview.mdx (L256-258)
```text
## Transaction fees

Pallet ISMP uses unsigned transactions for executing cross-chain messages. This means all cross-chain messages received are executed for free as unsigned transactions. The upside to this is that it cannot be exploited as a spam vector, since the transaction pool will check if the submitted extrinsics are valid before they are included in the pool. This validity check ensures that the transaction can be successfully executed and contains valid proofs. Malformed messages or those with invalid proofs are filtered out by the transaction pool validation logic preventing unnecessary processing and potential network congestion.
```

**File:** docs/content/developers/evm/bandwidth/overview.mdx (L8-16)
```text
Hyperbridge meters outbound traffic per `(source chain, app)`. Instead of paying a protocol fee on every dispatch, an app pre-pays for a tier and earns a byte allowance that drains as it sends messages. The allowance is enforced by the **bandwidth gate** on Hyperbridge — a hook the ISMP router consults on every inbound request from a source chain. When the gate is empty, the message is rejected.

Bandwidth is sold per **tier** (a byte budget × a time window) and per **month** (a multiplier on both). Purchases are made from any source chain by calling `purchase()` on the [`BandwidthManager`](https://github.com/polytope-labs/hyperbridge/blob/main/evm/src/apps/BandwidthManager.sol) contract; the contract dispatches a credit message to [`pallet-bandwidth`](https://github.com/polytope-labs/hyperbridge/blob/main/modules/pallets/bandwidth/src/lib.rs) on Hyperbridge, which mints a new subscription for the target `(chain, app)`.

## Why Bandwidth

Per-message protocol fees price each dispatch in isolation. That works for occasional cross-chain traffic but is awkward for apps that send a steady stream of small messages — every dispatch pays the same overhead and there's no way to commit upfront to a usage budget.

Bandwidth swaps that model for a subscription. An app buys a tier once, the pallet tracks the remaining byte balance, and the gate silently passes messages until the balance is exhausted. There's no per-message fee path on dispatch — the cost was paid at purchase time.
```
