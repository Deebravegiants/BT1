### Title
Unbounded in-memory `BidCache` growth via mempool `place_bid` transactions enables node memory-exhaustion DoS - (File: `modules/pallets/intents-coprocessor/rpc/src/lib.rs`)

### Summary
The intents-coprocessor RPC module maintains an in-process `BidCache` that is populated directly from the transaction-pool's "ready transaction" notification stream — before any block inclusion, fee payment finality, or validity check beyond basic pool acceptance. Any account able to submit a `place_bid` extrinsic (an unprivileged intent-solver/filler action) can cause this cache to grow without bound in size and in entry count, exactly analogous to the reported Discourse `SvgSprite` cache DoS, where attacker-influenced cache keys/values accumulate unbounded in server memory until the process is killed.

### Finding Description
`run_bid_watcher` subscribes to `pool.import_notification_stream()` and, for every transaction seen ready in the pool, calls `extract_bid` to pull `(commitment, filler, user_op)` out of any `place_bid` call, then unconditionally inserts it into the shared `BidCache`: [1](#0-0) 

`BidCache::insert` stores an unbounded `Vec<BidEntry>` per order commitment, keyed by attacker-supplied `filler` bytes, with no cap on:
- the number of distinct commitments tracked (`HashMap<H256, OrderBids>`),
- the number of distinct fillers per commitment (`entries: Vec<BidEntry>` grows once per unique filler), or
- the size of the cached `user_op` / `filler` byte vectors themselves (arbitrary `Vec<u8>` copied verbatim from the extrinsic). [2](#0-1) 

Cleanup only happens on a periodic timer and is keyed off `first_seen`, which is set once at the *first* insertion for a commitment and never refreshed by later inserts to the same commitment: [3](#0-2) 

`extract_bid` decodes the extrinsic and extracts the signer address plus the raw `user_op` bytes from the `place_bid` call with no size validation performed by the RPC layer itself: [4](#0-3) 

Because the cache is fed straight from the ready-transaction stream, an attacker does not need transactions to ever be included in a block — only to be accepted into the node's ready pool (e.g. cheaply-signed, low/zero-value calls with distinct signer/filler addresses and large `user_op` payloads up to the extrinsic size limit). Within one cleanup TTL window, an attacker can submit many unique `(filler, user_op)` pairs for the same or many different commitments, each triggering a fresh `HashMap`/`Vec` allocation that is retained until the TTL elapses. This is directly analogous to the SvgSprite bug class: attacker-controlled data is cached per-process with no bound on cardinality or payload size, and the mitigation ("only a concern when the actor is untrusted") does not apply here because `place_bid` submitters are explicitly unprivileged intent solvers/fillers, not admins.

### Impact Explanation
Every node running this RPC/tx-pool watcher (e.g. relayer or collator/full nodes serving the intents RPC) accumulates attacker-controlled cache memory proportional to attacker-submitted mempool traffic, not to any on-chain state or fee paid. Sustained submission of many `place_bid` transactions with large `user_op` payloads and unique fillers can exhaust node memory, causing process kills/restarts and denial of service to the bid-discovery RPC and any node sharing the process. This is a resource-exhaustion / route-availability issue — a node made unable to deliver messages/serve RPC due to OOM matches the "route unable to deliver messages" acceptance criterion, warranting Medium severity in line with the original Discourse advisory.

### Likelihood Explanation
Likelihood is moderate-to-high: `place_bid` is a normal, permissionless extrinsic intended for any solver to submit, and being accepted into a node's ready transaction pool (not finalized) is a much lower bar than achieving on-chain inclusion. An attacker only needs enough balance to pay pool-entry fees for many transactions with distinct signer/filler identities and can maximize `user_op` size up to the runtime's extrinsic size limit to accelerate memory growth within a single TTL window.

### Recommendation
Bound the `BidCache` deterministically:
- Cap the number of distinct commitments and the number of entries per commitment (e.g. LRU eviction or a hard `MAX_ENTRIES`/`MAX_BIDS_PER_ORDER`).
- Cap the byte length of cached `filler` and `user_op` before insertion, rejecting/discarding oversized entries.
- Refresh or independently track `first_seen`/expiry per entry (not just per commitment) so a steady trickle of distinct fillers cannot keep a commitment's bucket alive indefinitely.
- Consider validating the transaction's fee/signature economics before caching, so entering the ready pool alone is not sufficient to consume unbounded cache memory.

### Proof of Concept
1. Deploy multiple signer accounts each with minimal balance sufficient to have a `place_bid(commitment, user_op)` extrinsic accepted into the node's ready transaction pool (no block inclusion required).
2. For a fixed `commitment`, submit many transactions from distinct signer accounts (each becomes a unique `filler` via the signed address) with maximally-sized `user_op` byte payloads (up to the runtime's extrinsic length limit), all within one `BidCache` TTL window.
3. Observe `run_bid_watcher` inserting every one of these into `BidCache::bids[commitment].entries`, growing the `Vec<BidEntry>` and consuming memory proportional to `num_signers * max_user_op_size`, with no cap enforced by `BidCache::insert`.
4. Repeat concurrently across many distinct `commitment` values to also grow the outer `HashMap<H256, OrderBids>` without bound, driving the RPC node's memory usage up until it is OOM-killed.

### Citations

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L100-129)
```rust
/// In-memory bid cache.
pub struct BidCache {
	bids: RwLock<HashMap<H256, OrderBids>>,
	ttl: Duration,
}

impl BidCache {
	pub fn new(ttl: Duration) -> Self {
		Self { bids: RwLock::new(HashMap::new()), ttl }
	}

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

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L149-154)
```rust
	pub fn remove_expired(&self) -> Result<(), String> {
		let now = Instant::now();
		let mut bids = self.bids.write().map_err(|e| format!("BidCache lock poisoned: {e}"))?;
		bids.retain(|_commitment, order| now.duration_since(order.first_seen) < self.ttl);
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

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L350-371)
```rust
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
```
