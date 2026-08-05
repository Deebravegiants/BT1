Confirmed: the signing payload construction and RPC verification match the claim exactly, and `recipients` is never folded into the signed message anywhere in `submit_signing_payload` [1](#0-0) , in the RPC verification path [2](#0-1) , or in `HopDataPool::insert` which stores whatever `recipients` were passed regardless of the signature [3](#0-2) . The duplicate check is keyed only on `blake2_256(data)` and is bypassed once the prior entry is removed by `ack` [4](#0-3) , confirming the replay window described in the report.

Audit Report

## Title
Recipient list is not covered by the `hop_submit` signature, allowing signature replay to redirect/hijack pool entries to attacker-chosen recipients - (File: `substrate/client/hop/src/rpc.rs`, `substrate/client/hop/src/pool.rs`, `substrate/client/hop/src/types.rs`)

## Summary
`hop_submit` verifies the submission signature only over `blake2_256(HOP_SUBMIT_CONTEXT || blake2_256(data) || submit_timestamp)`, via `submit_signing_payload` [1](#0-0) , and never folds `recipients` into the signed payload before calling `HopDataPool::insert` [5](#0-4) . Because entries are content-addressed solely by `blake2_256(data)` and the duplicate-entry guard only blocks re-insertion while the original hash is still present in `index` [6](#0-5) , an attacker who has observed a previously-valid `(data, signer, signature, submit_timestamp)` tuple can resubmit it with an arbitrary `recipients` list once the original entry has been fully acked and removed [4](#0-3) , causing the entry to be accepted as authored by the original signer but addressable only by the attacker's chosen keys.

## Finding Description
The root cause is a signature/authorization mismatch: the cryptographic commitment covers `(data, submit_timestamp)` but the actual authorized action is "deliver `data` to `recipients`." `submit_signing_payload` hashes only the context tag, data hash, and timestamp [1](#0-0) . The RPC handler decodes `recipients` independently of signature verification and passes them straight to `pool.insert` without any binding check [7](#0-6) [8](#0-7) . `insert` accepts whatever recipient list is supplied, keyed by the content hash of `data` which is unrelated to `recipients` [3](#0-2) . The only defenses in place — domain separation (`HOP_SUBMIT_CONTEXT`/`HOP_CLAIM_CONTEXT`/`HOP_ACK_CONTEXT`) and content-hash-keyed duplicate rejection — do not address this: domain separation only prevents cross-operation replay, and the duplicate check is bypassed once `ack` removes the fully-claimed entry from `index`, freeing the hash for reinsertion [4](#0-3) . `ack`'s own inline comment even acknowledges this exact scenario ("the entry could have been removed and re-submitted with a different recipient list since Phase 1") [9](#0-8) , confirming the maintainers were aware resubmission with a different recipient list under the same signature is a recognized code path, not a hypothetical.

## Impact Explanation
Two concrete in-scope impacts follow directly from the code as written:
- **Redirection of intended-private delivery**: since the signature never binds recipients, replaying a captured tuple lets an attacker register themselves as the recipient for data whose original delivery target was someone else, then `hop_claim`/`hop_ack` it — a genuine confidentiality violation of the hand-off protocol's purpose.
- **Quota/accounting abuse charged to a third party**: `insert` computes `accounted = entry_accounted_size(data_len, recipients.len())` and charges it to `sender_id` derived from the original signer [10](#0-9) , so an attacker can replay with up to `MAX_RECIPIENTS` (256) recipients and inflate a victim's quota usage and shared pool capacity without their consent, purely by observing one prior submission.

## Likelihood Explanation
Exploitation requires only that the attacker have observed one prior `(data, signer, signature, submit_timestamp)` tuple (all of which are non-secret RPC parameters, since HOP is explicitly designed as a semi-public off-chain hand-off relay accepting submissions from many unprivileged accounts, evidenced by per-account rate limiting and quota tracking in `HopDataPool` [11](#0-10) ) and that the original entry has since been fully acked/removed or otherwise become reusable. No special privilege, admin role, or protocol violation is needed — this is triggerable by any RPC caller through the standard `hop_submit` method [12](#0-11) .

## Recommendation
Bind `recipients` (or a hash of the SCALE-encoded recipient list) into the signed payload in `submit_signing_payload`, and recompute/verify this binding in `HopRpcServer::submit` before calling `pool.insert`, so that a signature only ever authorizes the exact `(data, recipients, submit_timestamp)` triple it was created for.

## Proof of Concept
1. Alice calls `hop_submit(data, recipients=[Bob], signature=S, signer=Alice, submit_timestamp=T)`, which verifies via `submit_signing_payload` and is inserted at hash `H = blake2_256(data)` [8](#0-7) .
2. Bob calls `hop_claim`/`hop_ack`; once all recipients ack, `pool.rs::ack` removes the entry from `index`, freeing `H` [4](#0-3) .
3. An attacker who observed `(data, S, Alice-signer, T)` calls `hop_submit(data, recipients=[Attacker], signature=S, signer=Alice, submit_timestamp=T)`. `H` is absent from `index`, so `DuplicateEntry` does not fire; `S` verifies against the unchanged payload; the entry is reinserted charged to Alice's `sender_id` with `recipients=[Attacker]`.
4. The attacker calls `hop_claim`/`hop_ack` against the new entry and obtains `data`, despite never being an originally intended recipient.

### Citations

**File:** substrate/client/hop/src/types.rs (L317-324)
```rust
/// Compute the 32-byte payload signed at `hop_submit` time.
///
/// The runtime pallet re-derives this exact byte sequence to verify the
/// signature on-chain, so the construction must remain byte-identical to the
/// pallet's `signing_payload(data, submit_timestamp)`:
/// `blake2_256(HOP_SUBMIT_CONTEXT || blake2_256(data) || submit_timestamp.to_le_bytes())`.
pub fn submit_signing_payload(hash: &HopHash, submit_timestamp: u64) -> [u8; 32] {
	let mut buf = [0u8; HOP_SUBMIT_CONTEXT.len() + 32 + 8];
```

**File:** substrate/client/hop/src/rpc.rs (L67-75)
```rust
	#[method(name = "hop_submit", blocking)]
	fn submit(
		&self,
		data: Bytes,
		recipients: Vec<Bytes>,
		signature: Bytes,
		signer: Bytes,
		submit_timestamp: u64,
	) -> RpcResult<SubmitResult>;
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

**File:** substrate/client/hop/src/pool.rs (L79-102)
```rust
pub struct HopDataPool {
	/// In-memory metadata index (no blobs).
	index: Mutex<HashMap<HopHash, HopEntryMeta>>,
	/// Per-user byte usage tracked by sender id.
	///
	/// Counters live directly in the map and are charged via `charge_user`
	/// inside the read guard, so the reclamation pass in `cleanup_expired`
	/// (which holds `user_usage.write()` together with `index.lock()`) cannot
	/// interpose between a lookup and its `fetch_add`. Stale entries —
	/// counter 0 and no live index entry — are reclaimed by the same pass.
	user_usage: RwLock<HashMap<SenderId, AtomicU64>>,
	/// Maximum pool size in bytes (counts both data and per-entry metadata overhead).
	max_size: u64,
	/// Fixed hard per-user quota in bytes.
	max_user_size: u64,
	/// Current pool size in bytes (accounted size — includes metadata overhead).
	current_size: AtomicU64,
	/// Data retention period in seconds.
	retention_secs: u64,
	/// Root data directory containing blobs/ and meta/ subdirectories.
	data_dir: PathBuf,
	/// Per-account submit rate limiter.
	rate_limiter: Arc<RateLimiter>,
}
```

**File:** substrate/client/hop/src/pool.rs (L341-356)
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
```

**File:** substrate/client/hop/src/pool.rs (L362-387)
```rust
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
```

**File:** substrate/client/hop/src/pool.rs (L389-399)
```rust
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
```

**File:** substrate/client/hop/src/pool.rs (L624-625)
```rust
		// Phase 2: re-run the lookup against the current meta — the entry could
		// have been removed and re-submitted with a different recipient list since Phase 1.
```

**File:** substrate/client/hop/src/pool.rs (L637-649)
```rust
		// If all recipients have acked, remove the entry entirely.
		if meta.recipients.iter().all(|r| r.claimed) {
			let accounted = entry_accounted_size(meta.size, meta.recipients.len());
			let sender = meta.sender_id;
			index.remove(hash);
			self.current_size.fetch_sub(accounted, Ordering::Relaxed);
			self.release_user_quota(&sender, accounted);
			drop(index);

			// Delete files from disk (best-effort; orphans cleaned on restart).
			let _ = fs::remove_file(self.blob_path(hash));
			let _ = fs::remove_file(self.meta_path(hash));

```
