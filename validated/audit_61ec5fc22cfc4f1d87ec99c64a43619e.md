### Title
Content-hash-keyed HOP pool rejects legitimate distinct submissions with identical bytes, enabling submission-blocking DoS - (File: `substrate/client/hop/src/pool.rs`)

### Summary
The `sc-hop` (Hand-Off Protocol) node service stores blobs in `HopDataPool` keyed solely by `blake2_256(data)` [1](#0-0)  and rejects any submission whose content hash already exists in the pool with `HopError::DuplicateEntry` [2](#0-1) . This is structurally the same pattern flagged in the LineaRollup report: using a content hash as the sole cardinality/uniqueness key for a submission system, where the hashed payload can legitimately collide across distinct, unrelated submissions (different senders, different recipients, different intents), causing the second legitimate submission to be blocked outright rather than accepted as an independent entry.

### Finding Description
`HopDataPool::index` is a `HashMap<HopHash, HopEntryMeta>` where `HopHash = blake2_256(data)` [3](#0-2) . The on-disk layout is also purely content-addressed: blob and meta files are stored at paths derived only from the hash of the data [4](#0-3) . Nothing about the sender, recipient set, or submit time is folded into the key — those are stored only as metadata (`HopEntryMeta`) alongside the entry, keyed by the same hash [5](#0-4) .

Per the documented protocol, `hop_submit(data, recipients, signature, signer, submit_timestamp)` fails with `DuplicateEntry` (RPC error code 1003) whenever a blob with the same content hash is already resident in the pool [6](#0-5) . Critically, `recipients`, `signer`, and `submit_timestamp` are *not* part of the key that determines uniqueness — only the raw bytes of `data` are. The test `test_concurrent_duplicate_insert_keeps_winner_meta_on_disk` explicitly demonstrates this: two different senders (`SENDER_A`, `SENDER_B`) submitting identical content race for the same slot, and exactly one wins while the other receives `HopError::DuplicateEntry` [7](#0-6) .

This is the same root cause class as the LineaRollup issue: the report's `dataHash` is used as the mapping cardinality for compressed batch data that omits distinguishing per-block fields, so two semantically distinct submissions can hash identically and the second is treated as "already submitted." In HOP, the analog is direct and simpler to trigger: any two independent parties (or the same sender at two different times) who want to hand off *the exact same bytes* — e.g. a common fixed-size template, a zero-filled placeholder blob, a well-known constant payload, a previously-published (and now public) blob, or any data an attacker can predict/observe — will collide on the same `blake2_256(data)` key. Since the sender, recipient list, and signature are irrelevant to the dedup check, a completely unrelated submission with coincidentally/deliberately identical bytes silently blocks a legitimate submission until the first entry expires, is fully claimed/acked, or is promoted on-chain.

An attacker does not need any special privilege: `hop_submit` is a JSON-RPC method reachable by any account, subject only to per-account rate limiting and the runtime's `can_account_promote` authorization gate [8](#0-7) . If the attacker is themselves an authorized account (or can find/guess data that a victim is about to submit), they can front-run or pre-populate the pool with the identical bytes under their own recipient list, keeping the victim's genuinely distinct handoff attempt (same content, different recipients/intent) locked out with `DuplicateEntry` for up to the full retention period (`--hop-retention-secs`, default 24h) [9](#0-8) .

### Impact Explanation
An authorized HOP submitter can deny another authorized submitter's handoff of the same content by pre-submitting identical bytes to different recipients. Because the pool key ignores sender/recipient/signature/timestamp, the victim's `hop_submit` call fails with `DuplicateEntry` even though it is a completely independent, legitimate operation. This blocks node-level off-chain data availability for up to the pool's retention window, and — since near-expiry entries are auto-promoted on-chain via `HopPromoter` — can also interfere with the intended on-chain promotion path for the victim's data, since only the original submitter's metadata (signer, recipients, signature) is stored and promoted, not the victim's. This is a availability/DoS issue confined to the collator's off-chain HOP pool (not chain state directly), but it directly matches the vulnerability class in the report: hash-of-payload used as sole cardinality for submission acceptance, with no per-submission unique salt (nonce, sender, or recipient binding) folded into the key.

### Likelihood Explanation
Likelihood is realistic for any unprivileged-but-authorized user of a chain running `sc-hop`: content collisions require no cryptographic break — only that two independent parties submit bit-identical payloads, which is plausible for canonical/templated data (fixed-format vouchers, well-known constant blobs, zero-padded messages, previously-published data an attacker can copy) or can be deliberately engineered by an attacker who can observe or predict a victim's payload before submission. The pool's own concurrency test confirms that identical-content races between different senders are an expected, handled (but not prevented) condition [10](#0-9) .

### Recommendation
Do not use the raw content hash as the sole pool key/cardinality. Fold a per-submission unique component into the key (e.g., `blake2_256(data || signer || submit_timestamp)` or `blake2_256(data) + signer` as a composite key), matching the report's recommendation to include a unique component (analogous to the L2 batch number) rather than relying purely on payload hash for cardinality. At minimum, allow multiple independent entries with the same content hash to coexist (e.g., index by `(content_hash, signer)` or an appended nonce), so that unrelated submitters' legitimate handoffs cannot collide and block one another.

### Proof of Concept
1. Authorized account A calls `hop_submit(data=X, recipients=[R1], signature=sigA, signer=A, submit_timestamp=t1)` → succeeds, entry stored under `hash = blake2_256(X)`.
2. Authorized account B independently (and legitimately) wants to hand off the same bytes `X` to a different recipient set: `hop_submit(data=X, recipients=[R2], signature=sigB, signer=B, submit_timestamp=t2)`.
3. Because the pool key is `blake2_256(X)` only, step 2 fails with `HopError::DuplicateEntry` (RPC code 1003) even though B's request is a distinct, legitimate, independently-authorized operation, as reproduced by the existing test `test_concurrent_duplicate_insert_keeps_winner_meta_on_disk` [11](#0-10) .
4. B must wait until A's entry expires, is fully claimed/acked (deleting it), or is promoted on-chain before B can submit the same content — a DoS window of up to `--hop-retention-secs` (default 86400s).

### Citations

**File:** substrate/client/hop/README.md (L17-20)
```markdown
- **Disk-backed** — blobs are written to disk immediately, only metadata lives
  in RAM. The in-memory index is rebuilt from on-disk `.meta` files on restart.
- **Content-addressed** — entries are keyed by `blake2_256(data)`; duplicates
  are rejected at submit time.
```

**File:** substrate/client/hop/README.md (L123-124)
```markdown
| `--hop-max-user-size <MiB>` | 256 | Per-user hard cap (not scaled by active users) |
| `--hop-retention-secs <s>` | 86400 (24 h) | How long entries are kept before expiry |
```

**File:** substrate/client/hop/README.md (L158-167)
```markdown
Submit fails with:
- `DataTooLarge` if `data.len() > HopRuntimeApi::max_promotion_size()`.
- `NotAuthorized` if `HopRuntimeApi::can_account_promote(account_id, data_len)`
  returns `false` (where `account_id` is `signer.into_account()`). The runtime
  sees `data_len` so it can express size-tiered authorization policies on top
  of the absolute cap.
- `RateLimited` if the per-account submit-rate or bandwidth bucket is empty.

Size and authorization are both checked *before* signature verification so
oversized or unauthorized floods don't force crypto work.
```

**File:** substrate/client/hop/README.md (L196-200)
```markdown
|---|---|---|
| 1001 | `DataTooLarge` | Blob exceeds runtime-reported `max_promotion_size` |
| 1002 | `PoolFull` | Total pool capacity exhausted |
| 1003 | `DuplicateEntry` | A blob with this hash is already in the pool |
| 1004 | `NotFound` | No entry for this hash (expired, never submitted, or deleted after final ack) |
```

**File:** substrate/client/hop/src/types.rs (L54-95)
```rust
/// Metadata for a pool entry (stored in-memory index and on-disk .meta files).
#[derive(Debug, Clone, Encode, Decode)]
pub struct HopEntryMeta {
	/// On-disk format version; see `HOP_META_VERSION`.
	pub version: u8,
	/// Unix timestamp (seconds) at which this entry expires.
	pub expires_at: u64,
	/// Size in bytes
	pub size: u64,
	/// Intended recipients and their per-recipient ack state.
	///
	/// Using a `BoundedVec` means a corrupted / hostile on-disk `.meta` file with
	/// too many recipients fails to SCALE-decode and is discarded during startup
	/// recovery rather than being loaded into the in-memory index.
	pub recipients: RecipientVec,
	/// Account ID of the sender who submitted this entry.
	pub sender_id: SenderId,
	/// Whether this entry has been promoted to permanent on-chain storage.
	pub promoted: bool,
	/// `MultiSigner` of the account that signed the submission. The runtime pallet
	/// re-verifies the submit signature using this key when the unsigned promotion
	/// extrinsic lands on-chain.
	pub signer: MultiSigner,
	/// The user's `hop_submit` signature over `submit_signing_payload(blake2_256(data),
	/// submit_timestamp)`. Carried along for the runtime to re-verify; "submit implies
	/// consent to promote" is the protocol semantic.
	pub signature: MultiSignature,
	/// Submit-time wall-clock timestamp (ms since unix epoch) bound into the
	/// signing payload. The runtime rejects promotions whose timestamp is too far
	/// from on-chain time, so old `(data, signer, signature)` tuples cannot be
	/// replayed indefinitely.
	pub submit_timestamp: u64,
	/// Number of times the maintenance task has tried (and failed) to promote
	/// this entry. Used together with `next_promotion_attempt_at` for
	/// exponential back-off. Reset behavior: never reset — once an entry hits
	/// `MAX_PROMOTION_ATTEMPTS` it is left to expire normally.
	pub promotion_attempts: u8,
	/// Block height at which the next promotion attempt becomes eligible.
	/// `0` means "any tick"; non-zero means the maintenance task should skip
	/// this entry until the chain reaches this block.
	pub next_promotion_attempt_at: HopBlockNumber,
}
```

**File:** substrate/client/hop/src/types.rs (L170-171)
```rust
	#[error("Data already exists in pool")]
	DuplicateEntry,
```

**File:** substrate/client/hop/src/pool.rs (L79-81)
```rust
pub struct HopDataPool {
	/// In-memory metadata index (no blobs).
	index: Mutex<HashMap<HopHash, HopEntryMeta>>,
```

**File:** substrate/client/hop/src/pool.rs (L303-316)
```rust
	fn entry_path(data_dir: &Path, hash: &HopHash, subdir: &str, ext: &str) -> PathBuf {
		let hex = hex::encode(hash);
		data_dir.join(subdir).join(&hex[..2]).join(format!("{}.{}", hex, ext))
	}

	/// Path to the blob file for a given hash.
	fn blob_path(&self, hash: &HopHash) -> PathBuf {
		Self::entry_path(&self.data_dir, hash, BLOBS_DIR, BLOB_EXT)
	}

	/// Path to the meta file for a given hash.
	fn meta_path(&self, hash: &HopHash) -> PathBuf {
		Self::entry_path(&self.data_dir, hash, META_DIR, META_EXT)
	}
```

**File:** substrate/client/hop/src/pool.rs (L1882-1924)
```rust
	#[test]
	fn test_concurrent_duplicate_insert_keeps_winner_meta_on_disk() {
		use std::{sync::Barrier, thread};

		// Same content, different senders. The race-loser's meta must not end
		// up on disk; otherwise restart recovery would silently load it as
		// canonical for the entry.
		let dir = TempDir::new().unwrap();
		let pool = Arc::new(
			HopDataPool::new(
				1024 * 1024,
				1024 * 1024,
				100,
				dir.path().to_path_buf(),
				RateLimitConfig::disabled(),
			)
			.unwrap(),
		);

		let signer_a = MultiSigner::Ed25519(ed25519::Pair::from_seed(&[11u8; 32]).public());
		let signer_b = MultiSigner::Ed25519(ed25519::Pair::from_seed(&[22u8; 32]).public());
		let data = vec![0xCDu8; 4096];

		let barrier = Arc::new(Barrier::new(2));
		let (p1, d1, b1, s1) = (pool.clone(), data.clone(), barrier.clone(), signer_a.clone());
		let h1 = thread::spawn(move || {
			b1.wait();
			p1.insert(d1, bv(vec![s1]), SENDER_A, dummy_auth().0, dummy_auth().1, 0)
		});
		let (p2, d2, b2, s2) = (pool.clone(), data.clone(), barrier.clone(), signer_b.clone());
		let h2 = thread::spawn(move || {
			b2.wait();
			p2.insert(d2, bv(vec![s2]), SENDER_B, dummy_auth().0, dummy_auth().1, 0)
		});

		let r1 = h1.join().unwrap();
		let r2 = h2.join().unwrap();

		let (winner_hash, winner_sender) = match (&r1, &r2) {
			(Ok(h), Err(HopError::DuplicateEntry)) => (*h, SENDER_A),
			(Err(HopError::DuplicateEntry), Ok(h)) => (*h, SENDER_B),
			other => panic!("expected exactly one winner and one DuplicateEntry, got {other:?}"),
		};
```
