Based on my investigation, I found a genuine analog to the "unverified token accepted as an authoritative identity claim" bug class, but it requires an important caveat: I was unable to load `modules/pallets/ismp/src/host.rs` (the actual `store_request_receipt`/`store_response_receipt` implementation) in the final round due to a tool error, so the root-cause claim below rests on strong circumstantial evidence (the `RequestMessage`/`ResponseMessage` struct definitions, the child-trie storage primitives, and downstream consumers) rather than a direct read of that one function body.

### Title
Unverified `signer` field in ISMP `RequestMessage`/`ResponseMessage` is trusted as the authoritative "delivering relayer" identity for fee/reward accounting - (File: `modules/ismp/core/src/handlers/request.rs`)

### Summary
`pallet-ismp`'s `handle_unsigned` extrinsic is permissionless and unsigned (`ensure_none(origin)`), so there is no cryptographically-bound account tied to who submits a message batch [1](#0-0) . Inside the message itself, `RequestMessage`/`ResponseMessage` carry a free-form `signer: Vec<u8>` field which the handler passes straight into `host.store_request_receipt(&wrapped_req, &msg.signer)` / `host.store_response_receipt(...)` [2](#0-1) [3](#0-2) . This value is written verbatim into the `RequestReceipts`/`ResponseReceipts` child-trie storage [4](#0-3) , with no signature check performed at the point of storage in the handler.

### Finding Description
Downstream, this stored "relayer" byte-string is treated as ground truth proof of who delivered the message and is used to move funds: `pallet-relayer::decode_receipt_relayer` reads `RequestReceipts[commitment]` and, for substrate destinations, either uses the raw bytes directly as the payee address (when ≤32 bytes) or decodes them as a `Signature` and calls `.signer()` — which only extracts an embedded public key without verifying that signature against any actual delivery message [5](#0-4) . That derived address is then credited fees via `accumulate_fee_and_deposit_event` [6](#0-5)  and is the exact value checked against in the cross-chain `OutboundRequestDeliveryClaim` reward payout path (`decode_receipt_relayer` feeding `ensure!(recovered == delivered_by, ...)`) [7](#0-6) .

Contrast this with the EVM handler, where the equivalent receipt is populated from `_msgSender()`, which is cryptographically unforgeable because it derives from the transaction's ECDSA signature [8](#0-7) . On the substrate side there is no equivalent binding: because `handle_unsigned` has no signed origin, `msg.signer` is a self-declared, attacker-chosen byte string that the core handler never authenticates before persisting it as the canonical delivery-attribution record.

Some other incentive layers do perform proper verification before paying out (e.g. `messaging-incentives::relayer_for` and `consensus-incentives::on_executed` both cryptographically verify an sr25519 signature over the message body before minting/crediting) [9](#0-8) [10](#0-9) . This shows the codebase's own convention is that a "signer" claim must be signature-verified before being trusted for payment — but the core `RequestReceipts`/`ResponseReceipts` write path (and the `accumulate_fees`/outbound-claim read path that consumes it for substrate destinations ≤32 bytes) does not follow that convention.

### Impact Explanation
If confirmed by the actual `store_request_receipt` body (which I could not load in this session), this allows any unprivileged party submitting a valid `handle_unsigned` message batch with legitimate state/consensus proofs to set the `signer` field to an arbitrary 32-byte value and have that value permanently recorded as the "delivering relayer" for that request/response commitment. Since `accumulate_fees` and the outbound delivery-reward claim both pay out to whatever address is recorded in the receipt, this could let an attacker redirect relayer fees/rewards to an address they control (or to third parties, causing a griefing/fund-misdirection condition) without ever having performed real proof-of-delivery signature work matching the payload.

### Likelihood Explanation
Medium likelihood: the message-crafting step is fully within a relayer's control (they choose the `signer` bytes when constructing `RequestMessage`/`ResponseMessage`), and `handle_unsigned` is explicitly permissionless. The main mitigating factor is that the relayer submitting the message is presumably the same party who wants the fee, so in the common case the "self-declared" identity coincides with the real deliverer's intent — the real risk is that nothing prevents *any* value being asserted, undermining the intended "prove cryptographically who delivered this" model used elsewhere (EVM `_msgSender()`, sr25519-verified incentive pallets).

### Recommendation
Require `msg.signer` for substrate `RequestMessage`/`ResponseMessage` to be a verifiable signature (as already done in `messaging-incentives` and `consensus-incentives`) checked against a canonical message digest before it is persisted into `RequestReceipts`/`ResponseReceipts`, or otherwise bind the stored relayer identity to the actual extrinsic signer/origin rather than an unauthenticated payload field.

### Proof of Concept
Not directly reproducible in this session because I could not inspect the concrete body of `store_request_receipt`/`store_response_receipt` in `modules/pallets/ismp/src/host.rs` (tool call failed in the final iteration) to confirm there is truly zero verification at that exact call site. **This is the key open uncertainty** — a Devin session with full file access should read `modules/pallets/ismp/src/host.rs` to confirm whether `store_request_receipt` performs any signature check on `signer` before writing it to `RequestReceipts`. If it does not, the PoC is: craft a `RequestMessage` with a valid state proof but `signer = arbitrary_attacker_bytes`, submit via `handle_unsigned`, then call `claim_outbound_request_delivery_reward` / trigger `accumulate_fees` and observe the reward is paid to `arbitrary_attacker_bytes` rather than any cryptographically-proven deliverer.

### Citations

**File:** modules/pallets/ismp/src/lib.rs (L373-382)
```rust
		pub fn handle_unsigned(
			origin: OriginFor<T>,
			messages: Vec<Message>,
		) -> DispatchResultWithPostInfo {
			ensure_none(origin)?;

			Self::execute(messages.clone())?;

			Ok(().into())
		}
```

**File:** modules/ismp/core/src/handlers/request.rs (L108-112)
```rust
				if host.request_receipt(&wrapped_req).is_some() {
					Err(Error::DuplicateRequest { meta: wrapped_req.clone().into() })?
				}
				// Store request receipt to prevent reentrancy attack
				let signer = host.store_request_receipt(&wrapped_req, &msg.signer)?;
```

**File:** modules/ismp/core/src/handlers/response.rs (L99-102)
```rust
			if host.response_receipt(&response).is_some() {
				Err(Error::DuplicateResponse { meta: (&response).into() })?
			}
			let signer = host.store_response_receipt(&response, &msg.signer)?;
```

**File:** modules/pallets/ismp/src/child_trie.rs (L140-159)
```rust
impl<T: Config> RequestReceipts<T> {
	/// Returns the hashed storage key
	pub fn storage_key(key: H256) -> Vec<u8> {
		request_receipt_storage_key(key)
	}

	/// Get the provided key from the child trie
	pub fn get(key: H256) -> Option<Vec<u8>> {
		child::get(&ChildInfo::new_default(CHILD_TRIE_PREFIX), &Self::storage_key(key))
	}

	/// Insert the key and value into the child trie
	pub fn insert(key: H256, relayer: &[u8]) {
		child::put(&ChildInfo::new_default(CHILD_TRIE_PREFIX), &Self::storage_key(key), &relayer);
	}

	/// Remove the key from the child trie
	pub fn remove(key: H256) {
		child::kill(&ChildInfo::new_default(CHILD_TRIE_PREFIX), &Self::storage_key(key))
	}
```

**File:** modules/pallets/relayer/src/accumulate.rs (L322-351)
```rust
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

**File:** modules/pallets/relayer/src/accumulate.rs (L353-368)
```rust
	pub fn accumulate_fee_and_deposit_event(
		state_machine: StateMachine,
		address: Vec<u8>,
		fee: U256,
	) {
		let _ = Fees::<T>::try_mutate(state_machine, address.clone(), |inner| {
			*inner += fee;
			Ok::<(), ()>(())
		});

		Self::deposit_event(Event::<T>::AccumulateFees {
			address: sp_runtime::BoundedVec::truncate_from(address),
			state_machine,
			amount: fee,
		});
	}
```

**File:** modules/pallets/relayer/src/outbound_request.rs (L169-184)
```rust
		let delivered_by = Self::decode_receipt_relayer(destination, &raw)?;

		let msg = outbound_request_delivery_message(commitment, destination, payee);
		let recovered = signature.verify(&msg, None).map_err(|_| Error::<T>::InvalidSignature)?;
		ensure!(recovered == delivered_by, Error::<T>::OutboundRequestSignerMismatch);

		let treasury: T::AccountId =
			<T as Config>::TreasuryPalletId::get().into_account_truncating();
		let payee_account: T::AccountId = payee.into();
		<<T as pallet_ismp::Config>::Currency as Mutate<T::AccountId>>::transfer(
			&treasury,
			&payee_account,
			reward,
			Preservation::Preserve,
		)
		.map_err(|_| Error::<T>::OutboundRequestRewardTransferFailed)?;
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

**File:** modules/pallets/consensus-incentives/src/impls.rs (L108-122)
```rust
	fn on_executed(
		messages: Vec<MessageWithWeight>,
		events: Vec<IsmpEvent>,
	) -> DispatchResultWithPostInfo {
		let maybe_relayer_account = messages.get(0).and_then(|first_message| {
			if let Message::Consensus(consensus_msg) = &first_message.message {
				let data = sp_io::hashing::keccak_256(&consensus_msg.consensus_proof);
				Signature::decode(&mut &consensus_msg.signer[..])
					.ok()
					.and_then(|sig| sig.verify_and_get_sr25519_pubkey(&data, None).ok())
					.map(|pub_key| pub_key.into())
			} else {
				None::<[u8; 32]>
			}
		});
```
