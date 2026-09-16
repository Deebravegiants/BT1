### Title
Unbounded in-memory `BidCache` growth via mempool `place_bid` flood causes node OOM DoS - ([File: modules/pallets/intents-coprocessor/rpc/src/lib.rs])

### Summary
The Intents RPC service watches the transaction pool for `place_bid` extrinsics and caches every observed bid in an unbounded, in-process `HashMap<H256, OrderBids>` before the transaction is ever included in a block or validated against pallet-level checks (deposit balance, phantom-order rules, etc.). Any account able to get a signed extrinsic into the node's ready transaction pool can grow this map without limit — each entry carrying up to ~1MB of attacker-controlled `user_op` bytes — and cleanup only occurs on a periodic timer that prunes by age, not by count or size, mirroring the `@libp2p/gossipsub` `this.topics` unbounded-growth pattern from the reference advisory.

### Finding Description
`run_bid_watcher` subscribes to `pool.import_notification_stream()` and, for every transaction that becomes `ready_transaction`, decodes it purely at the mempool level via `extract_bid` and stores the result in `BidCache::insert` — with **no on-chain execution, no deposit reservation check, and no cap on either the number of distinct `commitment` keys or the number of `filler` entries per commitment**: [1](#0-0) 

`BidCache::insert` unconditionally creates a new `HashMap` entry for every unique commitment and pushes a new `BidEntry` (containing the full `user_op`, up to 1MB per the pallet's `place_bid` bound) for every unique filler on that commitment: [2](#0-1) 

The only reclamation mechanism is `remove_expired`, invoked on a fixed timer, which removes entries strictly by age (`first_seen` vs `ttl`), not by cache size or memory pressure — so any burst of bids arriving within one `ttl` window (or faster than the configured `cleanup_interval`) accumulates without bound, exactly like `handleReceivedSubscription`'s missing per-peer/topic cap in the referenced gossipsub advisory: [3](#0-2) 

Because `commitment` is attacker-chosen (`extract_bid` simply reads whatever `H256` the caller put in the `place_bid` call, with no requirement that it correspond to a real, existing order) and `user_op` accepts up to `ConstU32<1_048_576>` bytes per the pallet definition: [4](#0-3) 

an attacker can submit a stream of validly-signed `place_bid` extrinsics with unique random commitments and maximal `user_op` payloads. Each only needs to pass mempool validity (signature + nonce + fee availability) to reach `ready_transaction` and trigger `bid_cache.insert` — it does **not** need to be included in a block, nor does it need sufficient balance for the pallet's internal `Currency::reserve` deposit check (that check only runs at block-execution time inside `place_bid`, not during mempool validation): [5](#0-4) 

This is the same defect class as the gossipsub report: (1) no size/count cap at ingestion, (2) unbounded per-key growth (`Vec<BidEntry>` per commitment, `HashMap` keyed by attacker-chosen commitment), and (3) cleanup that is time-based only, not capacity-based, leaving the process vulnerable to bursty floods that outrun the cleanup interval.

### Impact Explanation
Each cached bid can carry up to ~1MB of heap (the `user_op` bound), which is a far larger per-entry amplification than the gossipsub PoC's ~260 bytes/topic. An attacker with one funded account and an incrementing nonce can submit a stream of `place_bid` extrinsics with unique commitments, each landing in the ready pool and being cached before failing pallet-level deposit checks at execution time (or never being included at all if evicted from the pool once the local mempool limit is reached — the `BidCache` entry persists regardless). Sustained submission can exhaust the Node.js/Rust process heap of any Hyperbridge node running the Intents RPC extension, causing an OOM crash — an availability impact on nodes serving intent-bid discovery to solvers/relayers, which is a core dependency for the Hyperbridge Intent Gateway solver flow.

### Likelihood Explanation
Likelihood is high for any node exposing this RPC service: no special privileges are required, only the ability to get a signed extrinsic into the ready transaction pool (ordinary account balance for fees), and the attack cost per cached MB is a single low-fee transaction rather than a full deposit-backed bid. The only friction is transaction fees and the local mempool's own transaction-count limits, but since caching happens on `import_notification_stream` (independent of eventual block inclusion or pallet-level validation), an attacker can keep replacing evicted mempool transactions with new low-fee ones to keep triggering cache growth over time.

### Recommendation
- Bound `BidCache` total size (max distinct commitments and/or total bytes) and evict least-recently-used or oldest entries once the cap is reached, rather than relying solely on TTL-based `remove_expired`.
- Cap the number of `entries` per commitment (mirroring on-chain limits) and reject/skip inserts beyond that cap.
- Consider only caching bids once mempool validation has also confirmed the filler has sufficient reservable balance for the deposit (or otherwise rate-limit inserts per source account) to raise attacker cost per cached byte.
- Run `remove_expired` (or a size-based eviction) proactively inside `insert` when the cache exceeds a threshold, not only on the fixed timer, so bursts within one `ttl`/`cleanup_interval` window cannot cause unbounded growth.

### Proof of Concept
1. Fund a single account with enough balance to pay transaction fees (deposit reservation for `place_bid` is not required, since it is only checked at execution time).
2. Submit a stream of signed `place_bid(commitment, user_op)` extrinsics with sequentially incrementing nonces, each using a freshly-random `commitment: H256` and `user_op` padded to the 1MB bound (`ConstU32<1_048_576>`), as accepted by: [6](#0-5) 
3. Each transaction only needs to reach `ready_transaction` in the node's pool (satisfying signature/nonce/fee checks) to trigger: [7](#0-6) 
4. `BidCache::insert` creates a new unbounded `HashMap` entry per unique commitment, retaining the full 1MB `user_op` per entry with no cap: [2](#0-1) 
5. Repeating step 2 faster than `cleanup_interval`, or simply sending enough bids within one `ttl` window, grows the cache size roughly linearly with attacker-submitted bytes (≈1MB heap per transaction), exhausting the RPC node's process memory before `remove_expired`'s next tick can run: [3](#0-2)

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

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L149-154)
```rust
	pub fn remove_expired(&self) -> Result<(), String> {
		let now = Instant::now();
		let mut bids = self.bids.write().map_err(|e| format!("BidCache lock poisoned: {e}"))?;
		bids.retain(|_commitment, order| now.duration_since(order.first_seen) < self.ttl);
		Ok(())
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

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L332-343)
```rust
		#[pallet::call_index(0)]
		#[pallet::weight(T::WeightInfo::place_bid())]
		pub fn place_bid(
			origin: OriginFor<T>,
			commitment: H256,
			user_op: BoundedVec<u8, ConstU32<1_048_576>>,
		) -> DispatchResult {
			let filler = ensure_signed(origin)?;

			// Validate user_op is not empty
			ensure!(!user_op.is_empty(), Error::<T>::InvalidUserOp);

```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L366-370)
```rust
			let deposit = Self::storage_deposit_fee();

			// Reserve the new deposit
			<T as Config>::Currency::reserve(&filler, deposit)
				.map_err(|_| Error::<T>::InsufficientBalance)?;
```
