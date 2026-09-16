This is exactly the confirmation needed: the `GetRequestsWithProof.address` field is an arbitrary, unauthenticated `Vec<u8>` supplied directly by whoever submits the `pallet_state_coprocessor::handle_unsigned` extrinsic. There is no signature, no proof, and no `msg.sender`/origin binding tying this address to the entity that actually did the work of assembling and relaying the GET-response proof. `handle_unsigned` accepts `OriginFor::None` [1](#0-0) , and `handle_get_requests` destructures `address` straight out of the caller-supplied struct [2](#0-1) , then mints reputation directly to that address after verifying only the request/response state proofs — never verifying that `address` corresponds to the account that produced/submitted the proof [3](#0-2) .

### Title
Unauthenticated `address` field in `GetRequestsWithProof` lets anyone mint relayer reputation to an arbitrary account - (File: `modules/pallets/state-coprocessor/src/impls.rs`)

### Summary
`pallet-state-coprocessor::handle_unsigned` is a feeless, unsigned extrinsic that anyone can submit with a valid GET-request/response proof pair. The struct also carries a free-form `address: Vec<u8>` field that the pallet trusts as "the relayer to credit" and mints `ReputationAsset` to it, with no signature or provenance check binding that address to the entity that actually produced the proof.

### Finding Description
`GetRequestsWithProof` declares `address` as simply "Address that should be credited with fees" [4](#0-3) . `handle_get_requests` verifies the source/response state proofs and inserts the responses, but the only use of `address` is to mint the messaging-incentives `ReputationAsset` directly to it, after converting it to a 32-byte account id — no cryptographic check ties this value to whoever crafted the state proofs or submitted the extrinsic: [5](#0-4) 

This is the same root-cause pattern as CVE-2019-12447: a privileged/feeless code path performs an action ("credit this identity") using an untrusted, caller-supplied identity value instead of the actual authenticated identity of the party performing the corresponding privileged operation (a working, `setfsuid`-equivalent binding is missing). Compare this with the sibling pallet `pallet-messaging-incentives`, which does the correct thing: it recovers the relayer's account by verifying an sr25519 signature over the message contents (`relayer_for`) rather than trusting a bare address field [6](#0-5) . `pallet-state-coprocessor` has no equivalent check.

Because `handle_unsigned` is validated only by `ensure_none` and proof correctness (no fee, no signer requirement) [7](#0-6) , any unprivileged party who is capable of assembling (or observing in the mempool/relayer infra and resubmitting) a valid `GetRequestsWithProof` can set `address` to their own account and collect the reputation mint intended for the entity that actually performed the delivery work, or credit an arbitrary third party at will.

### Impact Explanation
Reputation minted here is governed by `pallet-messaging-incentives`'s per-byte `MintPerByte` rate and shares `ReputationAsset` with the rest of the incentive system — the docs describe it as feeding relayer incentives/allowlisting semantics. An attacker who can submit (or front-run submission of) any valid GET response proof can arbitrarily choose the credited account, effectively minting unbacked/misattributed reputation to any address of their choosing without having contributed the corresponding relaying work, and can strip legitimate relayers of the credit for work they performed (a resource/accounting integrity break analogous to the file-ownership confusion in the CVE). This is a Medium-severity accounting-integrity bug: it does not directly move funds, but it corrupts the on-chain reputation ledger used to steer relayer incentives, which is a stated reward/accounting surface explicitly in scope.

### Likelihood Explanation
High reachability: `handle_unsigned` is feeless and callable by anyone, requiring only a syntactically valid `GetRequestsWithProof` with legitimate state proofs (which are "freely provided" per protocol design docs) — no signature over the `address` field, no relationship to `msg.sender`/origin is enforced anywhere in the call path.

### Recommendation
Bind `address` to a verified identity rather than trusting the raw bytes: require the submitter to sign the request/response commitments (mirroring `pallet-messaging-incentives::relayer_for`, which recovers the credited account from a signature over the message) and recover the credited account from that signature instead of accepting it as plain input; alternatively, remove per-call credit assignment from this pallet entirely and route reputation minting for GET-response delivery through the already-signature-verified `pallet-messaging-incentives` path.

### Proof of Concept
1. Observe (or independently assemble) any valid `GetRequestsWithProof` — legitimate source/response state proofs are public/derivable by any relayer per protocol design.
2. Submit `pallet_state_coprocessor::handle_unsigned(origin: None, message)` with `address` set to an attacker-controlled account instead of the account that actually produced the proof.
3. `handle_get_requests` verifies only the state proofs (unrelated to `address`) and, when `pallet_messaging_incentives::MintPerByte` is non-zero, mints `total_bytes * MintPerByte` of `ReputationAsset` directly to the attacker's chosen `address` [8](#0-7) , with no verification that this account did the corresponding work.

### Citations

**File:** modules/pallets/state-coprocessor/src/lib.rs (L87-104)
```rust
		/// This is an extension of the ISMP protocol to allow Hyperbridge perform state proof
		/// verification on behalf of its applications and provides the verified values in the
		/// overlay tree.
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

**File:** modules/pallets/state-coprocessor/src/impls.rs (L42-64)
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

impl<T: Config> Pallet<T>
where
	<T as frame_system::Config>::AccountId: From<[u8; 32]>,
	<T as pallet_ismp::Config>::Balance: Into<u128>,
{
	pub fn handle_get_requests(
		GetRequestsWithProof { requests, source, response, address }: GetRequestsWithProof,
	) -> Result<(), Error> {
```

**File:** modules/pallets/state-coprocessor/src/impls.rs (L156-186)
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
```

**File:** modules/pallets/messaging-incentives/src/lib.rs (L137-153)
```rust
	/// Recover the relayer's account from the sr25519 signature on a
	/// `Message`'s `signer` field. Returns `None` if the message has
	/// no signer (e.g. consensus messages) or the signature is bad.
	fn relayer_for(message: &Message) -> Option<T::AccountId> {
		let (signer, signed) = match message {
			Message::Request(msg) =>
				(&msg.signer, sp_io::hashing::keccak_256(&msg.requests.encode())),
			Message::Response(msg) =>
				(&msg.signer, sp_io::hashing::keccak_256(&msg.requests.encode())),
			_ => return None,
		};
		Signature::decode(&mut &signer[..])
			.ok()?
			.verify_and_get_sr25519_pubkey(&signed, None)
			.ok()
			.map(T::AccountId::from)
	}
```
