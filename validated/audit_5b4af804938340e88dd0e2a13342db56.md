## Title
Unbounded, TTL-based `BidCache` growth from transaction-pool-only validated `place_bid` extrinsics enables memory exhaustion DoS on Hyperbridge full/collator nodes - (File: `modules/pallets/intents-coprocessor/rpc/src/lib.rs`)

### Summary
The `pallet-intents-coprocessor` RPC subsystem watches the node's transaction pool for `place_bid` extrinsics and caches their contents in an in-memory `BidCache` as soon as a transaction becomes "ready" in the pool [1](#0-0) . This caching happens **before** the pallet's actual dispatch-time validation (deposit reservation, balance checks, phantom-order window/duplicate checks) ever runs [2](#0-1) , and the cache itself has no cap on the number of entries or total bytes held — only a 300-second TTL swept every 60 seconds [3](#0-2) . Each cached entry can carry a `user_op` payload of up to 1 MB, matching the pallet's `BoundedVec<u8, ConstU32<1_048_576>>` bound [4](#0-3) . This is the same bug class as Lighthouse's gossip-cache OOM: a validation-agnostic cache admits attacker-controlled payloads before real (business-logic) validation, and its retention window is decoupled from the bounded resource (the transaction pool) that feeds it, allowing amplification.

### Finding Description
`run_bid_watcher` subscribes to `pool.import_notification_stream()`, which fires whenever a transaction becomes "ready" in the transaction pool — i.e., it has passed only `ValidateUnsigned`/`SignedExtension` checks (nonce ordering, signature, fee affordability) — not the pallet's dispatch body: [5](#0-4) 

For every such transaction it decodes a `place_bid` call via `extract_bid` and unconditionally inserts it into `BidCache`: [6](#0-5) 

`BidCache::insert` has no bound on:
- the number of distinct `commitment` keys in the `HashMap`,
- the number of `entries` (fillers) per commitment,
- the total bytes cached (each `user_op` can be up to 1 MB).

Eviction is purely time-based (`remove_expired`, using `first_seen` and a fixed 300s TTL, invoked every 60s) [7](#0-6) , completely decoupled from whether the underlying transaction is still in the pool, was replaced/evicted, or ever gets included in a block.

The real validation for a bid — sufficient balance for the storage deposit, phantom-order bid-window/duplicate checks — only happens when the pallet's `place_bid` extrinsic actually executes in a block: [2](#0-1) 

Because the transaction pool's own byte/count limits bound how many "ready" 1 MB transactions can be concurrently present, but say nothing about the *cache's* retention, an attacker can churn signed `place_bid` extrinsics (from many disposable, minimally-funded accounts — pool validation only needs fee affordability, not the deposit) through the pool faster than the pool's natural capacity, each triggering a new `import_notification_stream` event and thus a new ~1 MB cache insertion that persists for the full 300-second TTL — regardless of whether the pool evicted/replaced/dropped the underlying transaction moments later. This decouples the attacker's cost (pool-bounded, cheap, replaceable transactions) from the victim's memory cost (TTL-bounded accumulation), exactly mirroring the reported Lighthouse cache-before-validation amplification.

### Impact Explanation
An unprivileged intent solver / bandwidth purchaser (any account able to sign and submit a `place_bid` extrinsic with minimal funds to cover the pool's fee-affordability check) can drive sustained growth of an unbounded, un-rate-limited in-memory structure on every Hyperbridge full/collator node running this RPC extension, without needing the bids to ever land on-chain. Sustained submission over the 300-second TTL window can accumulate memory far beyond the transaction pool's own configured byte limit, leading to node memory exhaustion / crash — a DoS against the intents/bid-discovery RPC path and, transitively, against node availability more broadly (nodes hosting this pallet's RPC also participate in consensus/block production).

### Likelihood Explanation
Likelihood is high: no privileged role or governance action is required, the RPC watcher and `BidCache` are always active whenever `pallet-intents-coprocessor`'s RPC is wired up (`parachain/node/src/service.rs`), `place_bid` extrinsics are unsigned-origin-free (regular signed calls, `ensure_signed`) available to any account, and the only real cost to the attacker is a transaction fee for calls that never need to succeed on-chain — they only need to become "ready" in the pool momentarily.

### Recommendation
- Bound `BidCache` by total memory/byte budget and/or a maximum number of tracked commitments and entries-per-commitment, evicting oldest/lowest-priority entries once the cap is reached (independent of TTL).
- Do not cache from pool "ready" notifications alone; require at least a cheap pre-check (e.g., a lightweight existence/affordability probe for the claimed deposit) before admitting a bid into the cache, or cap payload size cached per unique account until the corresponding extrinsic is actually included in a block.
- Tie cache entry lifetime to the transaction's continued presence in the pool (drop the cache entry when the transaction leaves the pool via `pool.status()`/removal notifications) rather than a fixed TTL that outlives pool eviction.

### Proof of Concept
1. Fund N throwaway accounts with only enough balance to satisfy the transaction pool's fee-affordability check for a `place_bid` call (not the on-chain storage deposit).
2. From each account, submit a `place_bid(commitment_i, user_op)` extrinsic where `user_op` is close to the 1 MB bound (`BoundedVec<u8, ConstU32<1_048_576>>`), using a fresh random `commitment_i` per transaction.
3. Each transaction reaches "ready" state in the pool and is picked up by `run_bid_watcher`'s `import_notification_stream`, causing `bid_cache.insert` to store up to 1 MB per entry [8](#0-7) .
4. Repeat submission continuously for the 300-second TTL window at a rate exceeding the pool's steady-state capacity (transactions can be allowed to be evicted/replaced in the pool without affecting the cache, since eviction is not observed by the cache).
5. Observe the node's `BidCache` memory footprint grow well beyond the transaction pool's configured byte limit, unbounded by any cap in `modules/pallets/intents-coprocessor/rpc/src/lib.rs`, until process memory exhaustion.

### Citations

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L16-17)
```rust
//! Watches the transaction pool for `place_bid` extrinsics, exposing them
//! over RPC before block inclusion for sub-second bid discovery.
```

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

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L345-371)
```rust
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
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L334-337)
```rust
		pub fn place_bid(
			origin: OriginFor<T>,
			commitment: H256,
			user_op: BoundedVec<u8, ConstU32<1_048_576>>,
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L339-370)
```rust
			let filler = ensure_signed(origin)?;

			// Validate user_op is not empty
			ensure!(!user_op.is_empty(), Error::<T>::InvalidUserOp);

			// Phantom orders have stricter rules: one bid per filler, no updates, and only
			// within the configured acceptance window after the order was registered. Every
			// chain's active order is checked, not just the most recently generated one.
			if let Some(active) = CurrentPhantomOrder::<T>::get() {
				if let Some((_, info)) = active.iter().find(|(c, _)| *c == commitment) {
					let window: BlockNumberFor<T> = Self::phantom_bid_window().into();
					ensure!(
						frame_system::Pallet::<T>::block_number() <= info.created_at_block + window,
						Error::<T>::PhantomOrderBidWindowClosed
					);
					ensure!(
						!Bids::<T>::contains_key(&commitment, &filler),
						Error::<T>::DuplicatePhantomBid
					);
				}
			}

			// If a bid already exists, unreserve the old deposit first
			if let Some(old_deposit) = Bids::<T>::get(&commitment, &filler) {
				<T as Config>::Currency::unreserve(&filler, old_deposit);
			}

			let deposit = Self::storage_deposit_fee();

			// Reserve the new deposit
			<T as Config>::Currency::reserve(&filler, deposit)
				.map_err(|_| Error::<T>::InsufficientBalance)?;
```

**File:** parachain/node/src/service.rs (L291-303)
```rust
	let bid_cache = Arc::new(pallet_intents_rpc::BidCache::new(Duration::from_secs(300)));
	let (bid_sender, _) = tokio::sync::broadcast::channel::<pallet_intents_rpc::RpcBidInfo>(256);

	task_manager.spawn_handle().spawn(
		"intents-bid-watcher",
		"intents",
		pallet_intents_rpc::run_bid_watcher::<_, _, T, Extra>(
			transaction_pool.clone(),
			bid_cache.clone(),
			bid_sender.clone(),
			Duration::from_secs(60),
		),
	);
```
