## Title
Unverified relayer identity in `Signature::signer()` lets any relayer claim another account's rewards/receipts without proving key ownership - (File: modules/pallets/ismp/src/host.rs)

### Summary
`extract_signer` in `pallet-ismp`'s `IsmpHost` implementation, and `Signature::signer()` in the shared crypto crate, extract the "relayer" identity that gets persisted into request/response receipts and event payloads without cryptographically verifying that the submitter actually controls that identity.

### Finding Description
`store_request_receipt` and `store_response_receipt` call `extract_signer(signer)` to determine whose account should be credited as the delivering relayer: [1](#0-0) 

`extract_signer` itself only decodes a `Signature` and calls `.signer()` when the byte length is `> 32`; for anything `<= 32` bytes it just returns the raw bytes verbatim, with **no verification at all**: [2](#0-1) 

Even in the `> 32` branch, `Signature::signer()` does not verify anything — it just returns the embedded public key/address field from whichever `Signature` variant was decoded, with zero relation to `Signature::verify()`/`verify_sr25519`/`verify_and_get_sr25519_pubkey`, which are the only methods that actually check a signature against a message: [3](#0-2) 

Since `pallet_ismp::Call::handle_unsigned` is dispatched with `ensure_none(origin)` (i.e., unsigned, callable by anyone) and the request/response handlers only pass `msg.signer` straight to `store_request_receipt`/`store_response_receipt` without ever calling `Signature::verify`, an attacker submitting a `RequestMessage`/`ResponseMessage` can put an arbitrary 32-byte (or shorter) value, or an arbitrary `Signature::Sr25519/Ed25519/Evm { public_key/address, signature: garbage }` blob, as `signer`. `extract_signer`/`Signature::signer()` will happily accept it and record it as the "relayer" without the caller ever proving possession of the corresponding private key: [4](#0-3) 

This identity is later relied upon by fee/incentive accounting logic downstream, e.g. `pallet-messaging-incentives`'s `relayer_for`, which *does* call `verify_and_get_sr25519_pubkey` to recover the signer for minting purposes — showing that other pallets in the same codebase correctly treat `signer` as attacker-controlled and verify it: [5](#0-4) 

That contrasts with `pallet-ismp`'s own `store_request_receipt`/`store_response_receipt`, which persist the unverified identity directly into the on-chain receipt (`child_trie::RequestReceipts`, `ResponseReceipts`) and into the `PostRequestHandled`/`RequestResponseHandled` events' `relayer` field, which is the canonical relayer-of-record used elsewhere in the protocol (e.g. `should_charge_fee_for_request` test, consensus-incentive test `test_incentivize_relayer`) for economic accounting: [6](#0-5) 

This is directly analogous to the Flask-AppBuilder CVE-2021-41265 bug class: an unprivileged actor supplies a "credential-like" field (the FAB REST auth token / here, the `signer` blob) that the system treats as authenticated identity without actually performing the underlying cryptographic check, letting the actor authenticate/act as someone else.

### Impact Explanation
Any relayer/attacker submitting the free, unsigned `handle_unsigned` extrinsic (`ensure_none` origin — reachable by literally anyone) can forge the `signer` field of a `RequestMessage`/`ResponseMessage` and have `pallet-ismp` record an arbitrary victim account as the request/response receipt's relayer and as the `relayer` field in the emitted `PostRequestHandled`/`RequestResponseHandled` events, without ever proving ownership of that account's key. Any downstream logic in the protocol or its applications that trusts `pallet-ismp`'s stored receipt/`relayer` field (as opposed to independently re-verifying the signature, the way `messaging-incentives` does) as proof-of-delivery for reward/fee accounting can be tricked into crediting or misattributing rewards to an account that never delivered anything — a form of unauthorized/forged relayer identity that maps to CWE-287 Improper Authentication and can lead to theft/misdirection of relayer rewards.

### Likelihood Explanation
High reachability: `handle_unsigned` is explicitly designed to be callable by anyone with no signature on the extrinsic itself, and nothing in `handle`/`store_request_receipt`/`store_response_receipt` calls `Signature::verify` on the embedded `signer` bytes before persisting them as the relayer of record — only membership-proof validity of the requests/responses is checked, not the `signer` field's authenticity.

### Recommendation
In `extract_signer` (and generally anywhere `pallet-ismp` derives the persisted "relayer" identity from `msg.signer`), require and check a real signature over the request/response batch (as `messaging-incentives::relayer_for` already does via `verify_and_get_sr25519_pubkey`) rather than trusting `Signature::signer()`/raw bytes. Any consumer of the `relayer` field stored in `RequestReceipts`/`ResponseReceipts` or emitted in `PostRequestHandled`/`RequestResponseHandled` for reward/fee purposes should not assume it is cryptographically attested unless `pallet-ismp` itself performs that verification at the point of storage.

### Proof of Concept
1. Construct a `RequestMessage` (or `ResponseMessage`) with valid requests/proof so it passes membership verification.
2. Set `signer` to an arbitrary 32-byte value equal to a victim's `AccountId` (or to an `Signature::Sr25519 { public_key: victim_pubkey, signature: <any bytes> }` blob).
3. Submit via `pallet_ismp::Pallet::<T>::handle_unsigned(RuntimeOrigin::none(), vec![message])` — this is exactly the unsigned-origin call path exercised by tests such as `should_charge_fee_for_request` and `test_incentivize_relayer`.
4. Observe that `extract_signer` returns the victim's bytes unchanged (≤32 byte path) or `Signature::signer()` returns the embedded, unverified public key (>32 byte path), which is then stored as the `relayer` in `RequestReceipts`/`ResponseReceipts` and emitted in the `PostRequestHandled`/`RequestResponseHandled` events — with no signature check ever performed against the request/response payload.

### Citations

**File:** modules/pallets/ismp/src/host.rs (L261-283)
```rust
	fn store_request_receipt(&self, req: &Request, signer: &Vec<u8>) -> Result<Vec<u8>, Error> {
		let signer = extract_signer(signer)?;

		let hash = hash_request::<Self>(req);
		child_trie::RequestReceipts::<T>::insert(hash, &signer);
		Ok(signer)
	}

	fn store_response_receipt(
		&self,
		res: &GetResponse,
		signer: &Vec<u8>,
	) -> Result<Vec<u8>, Error> {
		let signer = extract_signer(signer)?;

		let hash = hash_request::<Self>(&res.request());
		let response = hash_response::<Self>(&res);
		child_trie::ResponseReceipts::<T>::insert(
			hash,
			ResponseReceipt { response, relayer: signer.clone() },
		);
		Ok(signer)
	}
```

**File:** modules/pallets/ismp/src/host.rs (L351-359)
```rust
fn extract_signer(signer: &[u8]) -> Result<Vec<u8>, Error> {
	if signer.len() > 32 {
		Signature::decode(&mut signer.as_ref())
			.map(|sig| sig.signer())
			.map_err(|_| Error::SignatureDecodingFailed)
	} else {
		Ok(signer.to_vec())
	}
}
```

**File:** modules/utils/crypto/src/verification.rs (L97-115)
```rust
	pub fn verify_and_get_sr25519_pubkey(
		&self,
		msg: &[u8; 32],
		public_key_op: Option<Vec<u8>>,
	) -> Result<[u8; 32], anyhow::Error> {
		match self {
			Signature::Sr25519 { public_key, signature } =>
				Self::verify_sr25519(signature, public_key, msg, &public_key_op),
			_ => Err(anyhow!("Signature is not of type Sr25519")),
		}
	}

	pub fn signer(&self) -> Vec<u8> {
		match self {
			Signature::Evm { address, .. } => address.clone(),
			Signature::Sr25519 { public_key, .. } => public_key.clone(),
			Signature::Ed25519 { public_key, .. } => public_key.clone(),
		}
	}
```

**File:** modules/ismp/core/src/handlers/request.rs (L99-121)
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

**File:** modules/pallets/testsuite/src/tests/pallet_consensus_incentives.rs (L87-112)
```rust
#[test]
fn test_incentivize_relayer() {
	let mut ext = new_test_ext();
	ext.execute_with(|| {
		let host = Ismp::default();
		let state_machine_id = setup_state_machine();

		pallet_consensus_incentives::Pallet::<Test>::update_cost_per_block(
			RuntimeOrigin::root(),
			state_machine_id,
			100,
		)
		.unwrap();

		let (consensus_message, relayer_account) = setup_host_and_message(&host);

		pallet_ismp::Pallet::<Test>::handle_unsigned(
			RuntimeOrigin::none(),
			vec![consensus_message],
		)
		.unwrap();

		assert_eq!(Balances::balance(&relayer_account), UNIT + 4200);
		assert_eq!(Assets::balance(ReputationAssetId::get(), &relayer_account), 4200);
	})
}
```
