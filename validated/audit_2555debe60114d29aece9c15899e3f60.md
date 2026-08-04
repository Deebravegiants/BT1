Confirmed: `submit_signing_payload` (substrate/client/hop/src/types.rs:317-329) only binds `blake2_256(data)` and `submit_timestamp` into the signed payload — the `recipients` list is never part of what the sender signs. This is a direct analog of the audited bug: just as `PhiFactory.merkleClaim` verified only `minter_` while `ref_`/`artId_`/`imageURI` were taken from unchecked, attacker-controlled call arguments, `hop_submit` verifies only `(data_hash, submit_timestamp)` while `recipients` is an independent RPC parameter that any relaying/forwarding party can swap without invalidating the signature.

### Title
Recipient list is not covered by the `hop_submit` signature, allowing a relayer/MITM to redirect HOP data to attacker-controlled keys - (File: `substrate/client/hop/src/rpc.rs`, `substrate/client/hop/src/pool.rs`, `substrate/client/hop/src/types.rs`)

### Summary
The HOP hand-off protocol's `hop_submit` RPC accepts `data`, `recipients`, `signature`, `signer`, and `submit_timestamp` as independent parameters. The signature is verified only against `submit_signing_payload(hash(data), submit_timestamp)` [1](#0-0) . The `recipients` vector — the actual authorization list for who may later `hop_claim`/`hop_ack` the data — is never included in the signed payload, so it can be freely substituted by anyone who relays or intercepts a legitimately signed submission.

### Finding Description
`HopRpcServer::submit` decodes `recipients` from raw RPC bytes, independently decodes `signer`/`signature`, and checks the signature only against a payload built from the data hash and timestamp: [2](#0-1) 

`submit_signing_payload` explicitly excludes the recipient list from the domain-separated hash it computes: [1](#0-0) 

Because the signature only commits to `(blake2_256(data), submit_timestamp)`, a valid `(data, signature, signer, submit_timestamp)` tuple is valid for **any** `recipients` list. Anyone who observes a legitimately signed submission (e.g., a wallet-integrated relayer, a public gateway forwarding the RPC call, or a MITM on an unauthenticated JSON-RPC channel) can resubmit the same tuple with a `recipients` vector under their own control. `HopDataPool::insert` and `find_recipient_idx` never re-derive or bind the recipient set to anything the original sender committed to — the pool simply stores whatever `RecipientVec` arrived with the request [3](#0-2) , and later `claim`/`ack` calls only check that a supplied signature matches one of the stored `recipients` [4](#0-3) .

This mirrors the referenced C4 finding precisely: in `PhiFactory.merkleClaim`, the merkle proof verified only `minter_`, leaving `ref_`, `artId_`, and `imageURI` as attacker-controlled call parameters outside the cryptographic check. Here, the `hop_submit` signature verifies only `(data hash, submit_timestamp)`, leaving `recipients` as an attacker-controlled call parameter outside the cryptographic check.

### Impact Explanation
An attacker who intercepts or relays a genuine `hop_submit` call can hijack the hand-off: the original data (which may include sensitive payloads intended for specific ephemeral recipient keys) becomes claimable only by the attacker's own recipient key(s), since duplicate-hash submissions are rejected (`DuplicateEntry`) and the attacker's forged submission would need to land first, or the attacker races the legitimate one. The `sender_id`/`signer`/quota accounting still correctly attributes storage cost to the real sender (since `signer` is bound into the payload via `account_id`), but authorization to retrieve the data is fully decoupled from sender intent. This can result in theft/redirection of off-chain hand-off data to accounts not intended by the original signer.

### Likelihood Explanation
Exploitability requires the attacker to observe/intercept a valid `(data, signature, signer, submit_timestamp)` tuple before it's submitted to the pool (e.g., acting as or compromising a relay, or observing plaintext RPC traffic) and then race the resubmission with substituted recipients before the legitimate one lands (protected only by content-address `DuplicateEntry` de-duplication, not FCFS-safe against interception). This requires a specific interception position rather than being exploitable by a fully passive unprivileged user with no special network position, which is a meaningfully different threat model from the original Solidity finding (which required no interception — any minter with cred-approval could directly forge parameters in their own call). This distinction should be weighed when assessing whether this qualifies as in-scope/reachable for an unprivileged-attacker threat model.

### Recommendation
Bind the entire authorization surface — including `recipients` — into the signed `hop_submit` payload, e.g. `blake2_256(HOP_SUBMIT_CONTEXT || blake2_256(data) || encode(recipients) || submit_timestamp.to_le_bytes())`, and update `submit_signing_payload`/the runtime pallet's corresponding re-derivation in lockstep so promotion-time re-verification stays consistent.

### Proof of Concept
1. User A signs `submit_payload = submit_signing_payload(blake2_256(data), ts)` with their key and sends `(data, recipients=[R_A], signature, signer=A, ts)` to a relay/gateway for `hop_submit`.
2. An attacker observing this call (relay operator, or MITM on the RPC transport) resubmits `(data, recipients=[R_attacker], signature, signer=A, ts)` before the legitimate call lands, per `HopRpcServer::submit` [5](#0-4) .
3. The signature check passes because `recipients` is not part of the signed payload; `HopDataPool::insert` stores the attacker's recipient list.
4. The attacker calls `hop_claim`/`hop_ack` with a signature from `R_attacker` and retrieves the data [6](#0-5) ; the intended recipient's `hop_claim` now fails with `NotRecipient`/`NotFound`.

### Citations

**File:** substrate/client/hop/src/types.rs (L317-329)
```rust
/// Compute the 32-byte payload signed at `hop_submit` time.
///
/// The runtime pallet re-derives this exact byte sequence to verify the
/// signature on-chain, so the construction must remain byte-identical to the
/// pallet's `signing_payload(data, submit_timestamp)`:
/// `blake2_256(HOP_SUBMIT_CONTEXT || blake2_256(data) || submit_timestamp.to_le_bytes())`.
pub fn submit_signing_payload(hash: &HopHash, submit_timestamp: u64) -> [u8; 32] {
	let mut buf = [0u8; HOP_SUBMIT_CONTEXT.len() + 32 + 8];
	buf[..HOP_SUBMIT_CONTEXT.len()].copy_from_slice(HOP_SUBMIT_CONTEXT);
	buf[HOP_SUBMIT_CONTEXT.len()..HOP_SUBMIT_CONTEXT.len() + 32].copy_from_slice(hash.as_bytes());
	buf[HOP_SUBMIT_CONTEXT.len() + 32..].copy_from_slice(&submit_timestamp.to_le_bytes());
	blake2_256(&buf)
}
```

**File:** substrate/client/hop/src/rpc.rs (L150-219)
```rust
	fn submit(
		&self,
		data: Bytes,
		recipients: Vec<Bytes>,
		signature: Bytes,
		signer: Bytes,
		submit_timestamp: u64,
	) -> RpcResult<SubmitResult> {
		let recipient_keys: RecipientVec = recipients
			.into_iter()
			.map(|r| {
				MultiSigner::decode(&mut &r.0[..])
					.map(|signer| Recipient { signer, claimed: false })
					.map_err(|_| HopError::InvalidRecipientKey)
			})
			.collect::<Result<Vec<_>, _>>()?
			.try_into()
			.map_err(|v: Vec<Recipient>| HopError::TooManyRecipients {
				provided: v.len(),
				limit: MAX_RECIPIENTS as usize,
			})?;

		let signer =
			MultiSigner::decode(&mut &signer.0[..]).map_err(|_| HopError::InvalidSigner)?;
		let multi_sig = MultiSignature::decode(&mut &signature.0[..])
			.map_err(|_| HopError::InvalidSignature)?;

		let chain_info = self.client.info();
		let best_hash = chain_info.best_hash;

		let data_len = data.0.len();

		// Reject oversized payloads before the per-account authorization lookup so
		// a flood of too-big submits cannot force runtime state reads. The cap is
		// the runtime-declared `max_promotion_size`; the runtime is authoritative.
		let runtime_max = runtime_api::max_promotion_size::<Block, _>(&*self.client, best_hash)
			.map_err(HopError::from)?;
		if data_len > runtime_max as usize {
			return Err(HopError::DataTooLarge(data_len, runtime_max).into());
		}

		// Check authorization before verifying the signature: a flood of unauthorized
		// requests must not force a signature verification per submit.
		// `can_account_promote` returns false for any reason the runtime rejects:
		// unauthorized account or exhausted per-account quota.
		let account_id: AccountId32 = signer.clone().into_account();
		let authorized = runtime_api::can_account_promote::<Block, _>(
			&*self.client,
			best_hash,
			account_id.clone(),
			data_len as u32,
		)
		.map_err(HopError::from)?;
		if !authorized {
			return Err(HopError::NotAuthorized.into());
		}

		// Domain-separated payload so a submit signature cannot be replayed as claim/ack,
		// and bound to `submit_timestamp` so an old signature can't be replayed long
		// after the fact (the runtime enforces a tolerance window on the timestamp).
		let hash = H256(blake2_256(&data.0));
		let submit_payload = submit_signing_payload(&hash, submit_timestamp);
		if !multi_sig.verify(&submit_payload[..], &account_id) {
			return Err(HopError::InvalidSignature.into());
		}

		let sender_id: [u8; 32] = account_id.into();
		self.pool
			.insert(data.0, recipient_keys, sender_id, signer, multi_sig, submit_timestamp)?;
		Ok(SubmitResult { pool_status: self.pool.status() })
```

**File:** substrate/client/hop/src/pool.rs (L341-424)
```rust
	pub fn insert(
		&self,
		data: Vec<u8>,
		recipients: RecipientVec,
		sender_id: SenderId,
		signer: MultiSigner,
		signature: MultiSignature,
		submit_timestamp: u64,
	) -> Result<HopHash, HopError> {
		if recipients.is_empty() {
			return Err(HopError::NoRecipients);
		}
		let unique: BTreeSet<&MultiSigner> = recipients.iter().map(|r| &r.signer).collect();
		if unique.len() != recipients.len() {
			return Err(HopError::DuplicateRecipient);
		}

		if data.is_empty() {
			return Err(HopError::EmptyData);
		}

		let data_len = data.len() as u64;

		// Total accounted size includes bounded per-recipient metadata overhead so
		// a submitter cannot inflate memory via large recipient lists while the
		// capacity counter only tracks `data.len()`. Charge the rate limiter the
		// same accounted size, otherwise a 1-byte payload with 256 recipients
		// would cost ~10 KiB of pool capacity while only spending 1 byte of
		// bandwidth tokens — making the bandwidth dimension non-functional for
		// fan-out-heavy entries.
		let accounted = entry_accounted_size(data_len, recipients.len());

		// Rejected requests never reserve capacity — check before any atomic bump.
		if let Err(retry_after_secs) = self.rate_limiter.check(&sender_id, accounted) {
			return Err(HopError::RateLimited { retry_after_secs });
		}

		let previous_size = self.current_size.fetch_add(accounted, Ordering::Relaxed);
		if previous_size.saturating_add(accounted) > self.max_size {
			self.current_size.fetch_sub(accounted, Ordering::Relaxed);
			return Err(HopError::PoolFull(previous_size, self.max_size));
		}

		if let Err(e) = self.charge_user(&sender_id, accounted) {
			self.current_size.fetch_sub(accounted, Ordering::Relaxed);
			return Err(e);
		}

		let hash = H256(blake2_256(&data));

		// First duplicate check (read lock only).
		{
			let index = self.index.lock();
			if index.contains_key(&hash) {
				self.release_user_quota(&sender_id, accounted);
				self.current_size.fetch_sub(accounted, Ordering::Relaxed);
				return Err(HopError::DuplicateEntry);
			}
		}

		// Blob write is outside the lock — content-addressed bytes, racers
		// produce identical output, rename is atomic.
		let blob_path = self.blob_path(&hash);
		if let Err(e) = Self::write_atomic(&blob_path, &data) {
			self.release_user_quota(&sender_id, accounted);
			self.current_size.fetch_sub(accounted, Ordering::Relaxed);
			return Err(e);
		}

		let expires_at = SystemTime::now()
			.duration_since(UNIX_EPOCH)
			.unwrap_or_default()
			.as_secs()
			.saturating_add(self.retention_secs);
		let meta = HopEntryMeta::new(
			data_len,
			expires_at,
			recipients,
			sender_id,
			signer,
			signature,
			submit_timestamp,
		);
		let meta_bytes = meta.encode();
```

**File:** substrate/client/hop/src/pool.rs (L561-606)
```rust
	/// Decode `signature` and return the index of the matching recipient in
	/// `meta.recipients`. `context` is the operation's domain separator (claim
	/// / ack). Returning an index keeps a single implementation for both
	/// shared- and exclusive-borrow callers (`meta.recipients[idx]` works in
	/// either case).
	fn find_recipient_idx(
		meta: &HopEntryMeta,
		hash: &HopHash,
		signature: &[u8],
		context: &[u8],
	) -> Result<usize, HopError> {
		let multi_sig =
			MultiSignature::decode(&mut &signature[..]).map_err(|_| HopError::InvalidSignature)?;
		let payload = signing_payload(context, hash);

		meta.recipients
			.iter()
			.position(|r| multi_sig.verify(&payload[..], &r.signer.clone().into_account()))
			.ok_or(HopError::NotRecipient)
	}

	/// Claim data from the pool (read-only). Verifies the signature against recipient
	/// public keys. Returns the data if the signature matches a recipient.
	///
	/// This does NOT mark the recipient as claimed — call `ack` after receiving the data
	/// to confirm receipt.
	///
	/// Returns `AlreadyClaimed` if the recipient has already acked (data may be deleted).
	pub fn claim(&self, hash: &HopHash, signature: &[u8]) -> Result<Vec<u8>, HopError> {
		{
			let index = self.index.lock();
			let meta = index.get(hash).ok_or(HopError::NotFound)?;
			// Map NotRecipient → NotFound so callers cannot probe whether a hash
			// exists by observing different error codes.
			let idx = Self::find_recipient_idx(meta, hash, signature, HOP_CLAIM_CONTEXT)
				.map_err(|_| HopError::NotFound)?;

			// If this recipient already acked, the data may be gone.
			if meta.recipients[idx].claimed {
				return Err(HopError::AlreadyClaimed);
			}
		}
		// Read blob from disk and verify its content hash. May be gone if
		// concurrently acked and deleted, in which case we surface NotFound.
		self.read_and_verify_blob(hash)
	}
```
