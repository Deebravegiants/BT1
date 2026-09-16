This is a strong analog to the reported bug. The `handle_unsigned` extrinsic on `pallet-state-coprocessor` is callable by anyone (`ensure_none(origin)`, ValidateUnsigned) and takes a `GetRequestsWithProof` message whose `address` field — "the relayer's raw 32-byte public key" credited with fee/reputation rewards and recorded as the delivering relayer in events — is taken directly from the submitted payload with no cryptographic binding to the actual submitter or to any proof content. Exactly like the Parity `KeyFile.address` field, this `address` is deserialized data that is trusted at face value rather than derived/verified. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Unauthenticated `address` field in `GetRequestsWithProof` lets anyone mint relayer reputation and impersonate the delivering relayer - (File: modules/pallets/state-coprocessor/src/impls.rs)

### Summary
`pallet-state-coprocessor::handle_unsigned` accepts a `GetRequestsWithProof` message carrying an `address: Vec<u8>` field documented as "Address that should be credited with fees" / "the relayer's raw 32-byte public key." [4](#0-3)  This extrinsic is unsigned (`ensure_none(origin)`) and reachable by any submitter, mirroring the `validate_unsigned` re-verification path. [5](#0-4)  The `address` value is never checked against a signature, the state proof, or the actual proof submitter — it is only shape-checked (must decode to 32 bytes) before being used directly to mint reputation tokens and to populate the "relayer" field of the emitted `GetRequestHandled`/`ReputationMinted` events and the stored response receipt. [6](#0-5) 

### Finding Description
Just as the Parity `KeyFile.address` field was trusted at face value after deserialization instead of being re-derived from the key's secret, the `GetRequestsWithProof.address` field is trusted verbatim after SCALE-decoding a submitted unsigned extrinsic, instead of being cryptographically bound to whoever actually assembled and submitted the valid state proof. The state/membership proofs in `handle_get_requests` verify that the `GetRequest`/`GetResponse` data is correct, but they never bind `address` to the entity that produced the proof. Anyone observing a valid `GetRequestsWithProof` on the wire (or capable of constructing one, since the proofs are public state) can resubmit it — or a variant with the same proof but a different `address` — before the legitimate relayer, redirecting the reputation mint and the "delivering relayer" attribution to themselves. [7](#0-6) 

### Impact Explanation
`address` drives two persistent, protocol-visible outcomes with no reversal path: (1) `ReputationAsset::mint_into(&relayer, amount)`, an unbacked mint of reputation tokens to an attacker-chosen account scaled by the batch's byte size, and (2) the `GetRequestHandled`/response-receipt attribution recorded as which relayer "delivered" the response, which downstream reward/incentive accounting can consume as ground truth. [8](#0-7)  This is a concrete unbacked-mint / relayer-reward-misattribution primitive reachable from a single unsigned extrinsic.

### Likelihood Explanation
High. The extrinsic is unsigned and permissionless by design (`ensure_none`), and `GetRequestsWithProof` payloads (proofs + requests) are inherently public data once produced — front-running a legitimate relayer's submission with the same proof but a self-chosen `address` requires no privileged access, just mempool visibility, which any unprivileged relayer or bot already has.

### Recommendation
Do not trust `address` as freestanding, unauthenticated data. Bind it cryptographically to the actual proof submitter, e.g. by requiring a signature over the message (with the recovered signer becoming `address`), or by using the transaction's declared origin/relayer identity instead of an attacker-supplied field, consistent with how `pallet-relayer`'s `decode_receipt_relayer`/`RequestReceipts` derive relayer identity from proven on-chain receipts rather than a caller-supplied byte vector. [9](#0-8) 

### Proof of Concept
1. Observe (or independently construct, since all inputs are public state/proofs) a valid `GetRequestsWithProof` `{ requests, source, response, address: RELAYER_A }` about to be, or already, submitted to `handle_unsigned`.
2. Submit `handle_unsigned` with the identical `requests`/`source`/`response` but `address: ATTACKER`.
3. `handle_get_requests` runs the same state-proof verification (which never touches `address`) and succeeds. [10](#0-9) 
4. Reputation is minted to `ATTACKER` instead of `RELAYER_A`, and `GetRequestHandled`/response receipts record `ATTACKER` as the delivering relayer. [8](#0-7) 
5. If both submissions reach the pool, the mempool dedup tag is derived only from the sorted request hashes (not `address`), so whichever variant lands first — attacker's front-run — is what gets included, permanently misattributing the reward. [11](#0-10)

### Citations

**File:** modules/pallets/state-coprocessor/src/impls.rs (L42-55)
```rust
/// Message for processing state queries
#[derive(
	Debug, Clone, Encode, Decode, DecodeWithMemTracking, PartialEq, Eq, scale_info::TypeInfo,
)]
pub struct GetRequestsWithProof {
	/// The associated Get requests
	pub requests: Vec<GetRequest>,
	/// Proof of these requests on the source chain
	pub source: Proof,
	/// State proof of the requested values in the Get requests.
	pub response: Proof,
	/// Address that should be credited with fees
	pub address: Vec<u8>,
}
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L62-75)
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

```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L105-124)
```rust
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
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L156-192)
```rust

		// Mint reputation tokens to the named relayer. The address is the
		// relayer's raw 32-byte public key as supplied by the coprocessor.
		// A zero rate disables minting and a malformed address simply skips
		// the mint — we don't want a non-32-byte address to fail the whole
		// batch since the response insertion below has no dependency on it.
		// The per-byte rate and reputation asset are inherited from
		// `pallet-messaging-incentives` so both pallets share one source of truth.
		let rate = pallet_messaging_incentives::MintPerByte::<T>::get();
		if !rate.is_zero() && total_bytes > 0 {
			if let Ok(bytes32) = <[u8; 32]>::try_from(address.as_slice()) {
				let relayer: T::AccountId = bytes32.into();
				let bytes_balance: BalanceOf<T> = (total_bytes as u128).saturated_into();
				let amount = rate.saturating_mul(bytes_balance);
				if !amount.is_zero() {
					match <T as pallet_messaging_incentives::Config>::ReputationAsset::mint_into(
						&relayer, amount,
					) {
						Ok(_) => Pallet::<T>::deposit_event(Event::ReputationMinted {
							relayer,
							bytes: total_bytes,
							amount,
						}),
						Err(err) => log::warn!(
							target: "ismp",
							"state-coprocessor: reputation mint failed for {total_bytes}b: {err:?}",
						),
					}
				}
			}
		}

		for get_response in responses {
			host.store_response_receipt(&get_response, &address)?;
			Self::dispatch_get_response(get_response, address.clone())
				.map_err(|_| Error::Custom("Failed to dispatch get response".to_string()))?;
		}
```

**File:** modules/pallets/state-coprocessor/src/lib.rs (L90-104)
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
```

**File:** modules/pallets/state-coprocessor/src/lib.rs (L131-147)
```rust
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
```

**File:** modules/pallets/relayer/src/accumulate.rs (L317-351)
```rust
impl<T: Config> Pallet<T> {
	/// Decode a proven `RequestReceipts[commitment]` value into the delivering
	/// relayer's bytes. EVM stores the address RLP encoded, substrate stores the
	/// signer bytes or a signature to recover the signer from. Used by both fee
	/// accumulation and the outbound request delivery claim.
	pub fn decode_receipt_relayer(state_id: StateMachine, raw: &[u8]) -> Result<Vec<u8>, Error<T>> {
		match state_id {
			s if crate::is_pharos(&s) =>
				if raw.len() == 32 {
					Ok(Address::from_slice(&raw[12..]).0.to_vec())
				} else {
					Err(Error::<T>::ProofValidationError)
				},
			s if s.is_evm() => {
				use alloy_rlp::Decodable;
				Ok(Address::decode(&mut &*raw)
					.map_err(|_| Error::<T>::ProofValidationError)?
					.0
					.to_vec())
			},
			s if s.is_substrate() => {
				use codec::Decode;
				let bytes =
					<Vec<u8>>::decode(&mut &*raw).map_err(|_| Error::<T>::ProofValidationError)?;
				Ok(if bytes.len() > 32 {
					Signature::decode(&mut &*bytes)
						.map_err(|_| Error::<T>::SignatureDecodingError)?
						.signer()
				} else {
					bytes
				})
			},
			_ => Err(Error::<T>::MismatchedStateMachine),
		}
	}
```
