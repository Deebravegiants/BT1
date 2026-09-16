### Title
Uncontrolled memory growth in the intents-coprocessor RPC mempool bid cache - ([File: modules/pallets/intents-coprocessor/rpc/src/lib.rs])

### Summary
The `BidCache` used by the `intents_getBidsForOrder` / `intents_subscribeBids` RPC and its mempool watcher `run_bid_watcher` populates an in-memory `HashMap<H256, OrderBids>` from every `place_bid` extrinsic seen as "ready" in the transaction pool, before that extrinsic is ever included in a block. Neither the number of distinct order commitments nor the number of fillers per commitment is bounded, and the cache is only pruned by a time-based `remove_expired()` sweep — never by size. An unprivileged sender can flood the mempool with cheap `place_bid` transactions using attacker-chosen commitments and multiple signer accounts to grow this cache without bound until it is reclaimed by the TTL sweep, exhausting node memory. [1](#0-0) 

### Finding Description
`run_bid_watcher` subscribes to the transaction pool's `import_notification_stream()` and, for every transaction that becomes "ready" in the pool, decodes it as a `place_bid` call and inserts it into `BidCache` via `bid_cache.insert(commitment, filler, user_op)`: [2](#0-1) 

This happens purely at the mempool layer — i.e., the extrinsic only needs to pass ordinary signed-extrinsic validation (valid signature, correct nonce, enough balance for transaction fees) to become "ready." It does **not** need to be included in a block, and therefore never goes through `pallet_intents_coprocessor::place_bid`'s runtime logic, which is the only place a storage deposit (`StorageDepositFee`) is reserved and validated: [3](#0-2) 

`BidCache::insert` unconditionally grows the map: a new `H256` commitment always creates a new `OrderBids` entry, and each new filler for that commitment is pushed into its `entries` vector, with no bound on either dimension: [4](#0-3) 

The only eviction path is `remove_expired()`, called on a periodic timer (`cleanup_interval`), which removes an entry only once its TTL has elapsed — not based on cache size: [5](#0-4) 

There is no `MAX_BIDS`/size cap constant anywhere in this crate or pallet — the search for such a bound came back empty, confirming the cache is genuinely unbounded in size, unlike the analogous on-chain `Bids` storage which is gated behind a reserved balance deposit, or the on-chain-bid RPC path which is explicitly capped (`MAX_ON_CHAIN_BIDS: usize = 30`): [6](#0-5) 

This mirrors the CVE-2026-19014 bug class exactly: a caller-controlled input (here, an attacker-chosen order `commitment` plus a signer account acting as `filler`) grows an authorization/matching cache without bound, defeating any operator expectation of resource limits, because the mempool-observation cache sits upstream of and independent from the on-chain economic gate (the storage deposit) that would otherwise throttle growth.

### Impact Explanation
Any Hyperbridge full/RPC node running the intents bid-watcher can have its process memory grown without bound by an attacker who only needs to pay ordinary transaction fees (not the `StorageDepositFee` reserved by the runtime call) to get transactions accepted into the "ready" queue of the transaction pool. Because the cache key is an attacker-supplied `H256` commitment (no relation to an actual valid order is required for mempool acceptance) and the filler can be any of many cheaply funded accounts, the number of `(commitment, filler)` pairs cached is effectively unbounded until the TTL cleanup runs, which only bounds a rolling window, not the growth *within* that window. This is an uncontrolled resource consumption (memory-exhaustion DoS) issue on infrastructure nodes serving intent-solver/relayer bid discovery (`intents_getBidsForOrder`, `intents_subscribeBids`), potentially crashing or degrading nodes that solvers and relayers depend on to discover and race for fills — a denial of an availability-critical component of the intents pipeline. This qualifies as Medium severity resource exhaustion reachable by an unprivileged intent solver / bandwidth purchaser submitting transactions.

### Likelihood Explanation
High likelihood: submitting a `place_bid` extrinsic to the mempool requires only a valid signature and enough balance to cover the transaction fee — no minimum stake/deposit is checked at the mempool-acceptance stage, since the deposit-reservation logic lives inside the pallet's dispatch, which only runs on block inclusion, not on pool admission. An attacker can generate many signer accounts each funded with a small balance and many distinct commitment hashes, and repeatedly submit transactions faster than they expire out of the pool/cache, to grow `BidCache` unbounded.

### Recommendation
- Bound `BidCache` by total entry count (across all commitments) and/or per-commitment entry count, evicting oldest entries (e.g., LRU) once a configurable cap is reached, in addition to the existing TTL-based expiry.
- Consider requiring the observed mempool `place_bid` transaction to also satisfy a lightweight economic precondition before caching (e.g., checking the sender's free balance against the on-chain `StorageDepositFee` before inserting into `BidCache`), so mempool-level admission mirrors the on-chain deposit gate.
- Rate-limit cache insertions per source account/IP at the RPC/mempool-watcher layer.

### Proof of Concept
1. Fund a large number of accounts with the minimum balance needed to pay transaction fees (well below `StorageDepositFee`).
2. From each account, submit a `place_bid(commitment, user_op)` extrinsic with a unique, attacker-chosen `commitment` (no real order needs to exist) and a small `user_op` payload, at a rate high enough to keep ahead of the watcher's `cleanup_interval` TTL sweep.
3. Observe `run_bid_watcher`'s `import_notification_stream()` picking up each transaction as "ready" and calling `bid_cache.insert(...)` for every one, growing `BidCache`'s internal `HashMap<H256, OrderBids>` without bound, since neither `insert` nor `remove_expired` enforces a size cap — as shown in `modules/pallets/intents-coprocessor/rpc/src/lib.rs` lines 111-154 and 350-371.
4. Continue until the RPC/relayer node serving `IntentsApi` exhausts available memory or its `intents_getBidsForOrder` / `intents_subscribeBids` service becomes unresponsive.

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

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L228-235)
```rust
		let keys = self
			.client
			.storage_keys(best_hash, Some(&prefix_key), None)
			.map_err(runtime_error_into_rpc_error)?;

		const MAX_ON_CHAIN_BIDS: usize = 30;

		for key in keys.take(MAX_ON_CHAIN_BIDS) {
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

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L332-370)
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
