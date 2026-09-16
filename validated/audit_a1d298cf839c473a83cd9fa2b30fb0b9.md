The tool investigation shows a plausible analog, but I could not confirm the critical missing piece before running out of iterations: whether `place_bid` in `modules/pallets/intents-coprocessor/src/lib.rs` enforces any cap on the number of distinct fillers/bids per order commitment (i.e., a `MaxBidsPerOrder`-style bound). Without that confirmation I can't certify the root cause meets the "concrete" bar the validation rules require.

### Title
Unbounded per-commitment bid list in `BidCache` enables O(n²) CPU exhaustion of the intents RPC mempool watcher - (File: modules/pallets/intents-coprocessor/rpc/src/lib.rs)

### Summary
`BidCache::insert` in [1](#0-0)  stores, per order `commitment: H256`, an `OrderBids { entries: Vec<BidEntry> }` list of `(filler, user_op)` pairs. Every time `run_bid_watcher` ( [2](#0-1) ) observes a `place_bid` extrinsic in the transaction pool via `extract_bid`, it performs `order.entries.iter_mut().find(|e| e.filler == filler)` — a linear scan of the *entire* existing entry list for that commitment before appending. This is structurally the same bug class as CVE-2021-33582: work proportional to the number of prior insertions into a single bucket/key is repeated for every new insertion, i.e., O(n) work per insert and O(n²) total for n bids on one commitment, with no upper bound on n.

### Finding Description
`extract_bid` ( [3](#0-2)  derives the `filler` key directly from the signed extrinsic's address (`xt.preamble`), and the `commitment` from the `place_bid` call arguments — both fully attacker-controlled. An unprivileged actor can submit many `place_bid` extrinsics targeting the *same* `commitment` using many distinct signer accounts (only requiring whatever balance/fee the runtime demands to get the extrinsic into the ready pool — cheap on a permissionless chain, and unsigned/near-zero-cost accounts can be generated freely). Each accepted extrinsic triggers `bid_cache.insert(commitment, filler, user_op)`, and the linear `iter_mut().find` scan means the Nth bid for that commitment costs O(N) — with unbounded growth in `entries`, since `BidCache` has no cap on entries per commitment.

### Impact Explanation
This impacts the tesseract/RPC bid-watching task's tx-pool import stream (`stream.next()` loop), which single-threadedly processes every incoming mempool transaction. An attacker flooding a single commitment with many bids can degrade or stall the watcher's ability to process the import stream in a timely manner, delaying discovery of legitimate bids and impairing sub-second bid discovery for real fillers on that node — a denial-of-service against the intents/filler dispatch RPC path, analogous to the "many insertions into a single bucket" DoS described in CVE-2021-33582. It does not directly cause fund loss, but it can degrade the fill/bid discovery pipeline the intents solver path depends on.

### Likelihood Explanation
Medium. It requires submitting many signed extrinsics (cost scales with the runtime's transaction fee/mempool admission rules, which I did not fully verify — e.g., whether `place_bid` has a bond, minimum stake, or other admission cost that would raise the attack's economic cost). I was unable to confirm within the available searches whether the pallet-level `place_bid` call (`modules/pallets/intents-coprocessor/src/lib.rs`) enforces a cap on bids/fillers per order, which would materially change likelihood and severity — the pallet's on-chain `Bids` storage is a double-map, so it may not be the bottleneck, but the off-chain `BidCache` clearly lacks such a cap based on the code reviewed.

### Recommendation
Bound `OrderBids::entries` to a fixed maximum count per commitment in `BidCache::insert`, and/or replace the linear `iter_mut().find` scan with a `HashMap<filler, BidEntry>` keyed lookup (O(1) amortized) instead of a `Vec` with O(n) scan, mirroring the same fix pattern used elsewhere in the codebase for bounded eviction (e.g., `insert_bounded_state_commitment` in `modules/pallets/ismp/src/lib.rs`). Confirm and, if absent, add a cap on the number of distinct bids the on-chain `place_bid` extrinsic allows per commitment.

### Proof of Concept
1. Select a target order `commitment` (any valid or even not-yet-existing commitment works for the cache, since `BidCache::insert` does not validate against on-chain state).
2. Generate N distinct signer accounts capable of submitting a minimally-funded `place_bid(commitment, user_op)` extrinsic.
3. Submit all N extrinsics into the mempool of a node running `run_bid_watcher`.
4. Each accepted extrinsic drives `bid_cache.insert`, which performs an O(current-length) scan of `entries` for that commitment — total watcher CPU cost is O(N²) for N bids on the single commitment, delaying processing of the import-notification stream for all other legitimate bid/order traffic on that node.

Given I could not verify the on-chain bid-cap question, I recommend treating this as a candidate finding requiring confirmation of `place_bid`'s constraints in `modules/pallets/intents-coprocessor/src/lib.rs` before final triage.

### Citations

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L111-129)
```rust
	pub fn insert(
		&self,
		commitment: H256,
		filler: Vec<u8>,
		user_op: Vec<u8>,
	) -> Result<(), String> {
		let entry = BidEntry { filler: filler.clone(), user_op };

		let mut bids = self.bids.write().map_err(|e| format!("BidCache lock poisoned: {e}"))?;
		let order = bids
			.entry(commitment)
			.or_insert_with(|| OrderBids { first_seen: Instant::now(), entries: Vec::new() });
		if let Some(existing) = order.entries.iter_mut().find(|e| e.filler == filler) {
			*existing = entry;
		} else {
			order.entries.push(entry);
		}
		Ok(())
	}
```

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L295-324)
```rust
pub fn extract_bid<T, Extra>(encoded: &[u8]) -> Option<(H256, Vec<u8>, Vec<u8>)>
where
	T: pallet_intents_coprocessor::Config,
	T::RuntimeCall: frame_support::traits::IsSubType<pallet_intents_coprocessor::Call<T>>
		+ DecodeWithMemTracking,
	T::AccountId: Encode + From<[u8; 32]> + DecodeWithMemTracking,
	Extra: DecodeWithMemTracking,
{
	let xt = sp_runtime::generic::UncheckedExtrinsic::<
		sp_runtime::MultiAddress<T::AccountId, ()>,
		T::RuntimeCall,
		sp_runtime::MultiSignature,
		Extra,
	>::decode(&mut &encoded[..])
	.ok()?;

	let filler = match &xt.preamble {
		sp_runtime::generic::Preamble::Signed(address, _, _) => match address {
			sp_runtime::MultiAddress::Id(id) => id.encode(),
			_ => return None,
		},
		_ => return None,
	};

	match xt.function.is_sub_type()? {
		pallet_intents_coprocessor::Call::place_bid { commitment, user_op } =>
			Some((commitment.clone(), filler, user_op.to_vec())),
		_ => None,
	}
}
```

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L331-380)
```rust
pub async fn run_bid_watcher<P, Block, T, Extra>(
	pool: Arc<P>,
	bid_cache: Arc<BidCache>,
	bid_sender: broadcast::Sender<RpcBidInfo>,
	cleanup_interval: Duration,
) where
	Block: BlockT,
	P: TransactionPool<Block = Block> + 'static,
	T: pallet_intents_coprocessor::Config,
	T::RuntimeCall: frame_support::traits::IsSubType<pallet_intents_coprocessor::Call<T>>
		+ DecodeWithMemTracking,
	T::AccountId: Encode + From<[u8; 32]> + DecodeWithMemTracking,
	Extra: DecodeWithMemTracking + Send + 'static,
{
	use futures::StreamExt;

	let mut stream = pool.import_notification_stream();
	let mut timer = tokio::time::interval(cleanup_interval);

	loop {
		tokio::select! {
			Some(tx_hash) = stream.next() => {
				let tx = match pool.ready_transaction(&tx_hash) {
					Some(tx) => tx,
					None => continue,
				};

				let extrinsic_bytes = tx.data().encode();

				if let Some((commitment, filler, user_op)) = extract_bid::<T, Extra>(&extrinsic_bytes) {
					log::info!(
						target: LOG_TARGET,
						"bid in mempool for {commitment:?}",
					);
					if let Err(e) = bid_cache.insert(commitment, filler.clone(), user_op.clone()) {
						log::warn!(target: LOG_TARGET, "failed to cache bid: {e}");
						continue;
					}

					let _ = bid_sender.send(RpcBidInfo { commitment, filler, user_op });
				}
			}
			_ = timer.tick() => {
				if let Err(e) = bid_cache.remove_expired() {
					log::warn!(target: LOG_TARGET, "failed to clean bid cache: {e}");
				}
			}
		}
	}
}
```
