Based on my investigation, the strongest analog in-scope for this bug class (unbounded memory consumption from a client-side cache that isn't properly garbage-collected/bounded) is the `BidCache` in the Intents Coprocessor RPC watcher, reachable by any unprivileged filler submitting `place_bid` extrinsics to the mempool.

### Title
Unbounded, unauthenticated growth of the in-mempool `BidCache` before block inclusion enables memory-exhaustion DoS of Hyperbridge RPC nodes - (File: `modules/pallets/intents-coprocessor/rpc/src/lib.rs`)

### Summary
`run_bid_watcher` subscribes to the transaction-pool's `import_notification_stream` and, for every `place_bid` extrinsic that becomes "ready" in the pool (i.e. *before* block inclusion, and independent of whether it will ever be included or succeed), decodes it and inserts an entry into a process-wide `BidCache: RwLock<HashMap<H256, OrderBids>>`. The cache is only pruned by a periodic `remove_expired()` sweep gated by a TTL, not by any cap on the number of entries or total bytes held.

### Finding Description
`BidCache::insert` [1](#0-0)  unconditionally grows the `HashMap<H256, OrderBids>` (and the `Vec<BidEntry>` per commitment) for every distinct `(commitment, filler)` pair seen in a "ready" pool transaction — with no maximum entry count and no maximum total size. Because entries are added the moment a `place_bid` transaction is *ready in the pool*, not once it is finalized on-chain [2](#0-1) , an attacker can submit a large volume of valid-signature `place_bid` extrinsics (bounded only by nonce/fee/balance requirements, not by any per-order or global rate limit) each carrying up to a 1MB `user_op` payload [3](#0-2) , with distinct fabricated `commitment` values (arbitrary `H256`, no requirement that a real order exists) and/or distinct signer accounts as `filler`. Each such transaction adds a retained `BidEntry { filler, user_op }` to the cache that survives for the full `cleanup_interval`/TTL window, since eviction only happens on a fixed-interval timer tick calling `remove_expired()` [4](#0-3) , mirroring the CVE's pattern of an object whose lifetime is decoupled from consumption and only reclaimed on a lagging, unbounded-in-practice schedule. The cache size is thus proportional to (mempool import rate) × (TTL window) × (average `user_op` size up to 1MB), with no structural ceiling, so a sustained flood of cheap/rejectable `place_bid` transactions during the TTL window causes RSS on any node running this RPC handler (`IntentsRpcHandler`) to grow without bound relative to legitimate demand.

### Impact Explanation
This matches the CVE's CWE-401 (unrestricted memory consumption) class: an unprivileged party (any filler/solver with a funded account) can drive continuous growth of an in-memory structure on collator/RPC nodes serving `intents_getBidsForOrder`/`intents_subscribeBids`, degrading or crashing the node process (OOM), which denies service to the phantom-order bid-discovery pathway relied on by legitimate fillers and by the `IntentsCoprocessor` SDK client. This is a resource-exhaustion/DoS impact on infrastructure nodes rather than a fund-theft or consensus-safety bug.

### Likelihood Explanation
Likelihood is bounded by the cost of submitting many valid `place_bid` extrinsics (deposit reservation via `Currency::reserve`, per-account nonce sequencing, and normal transaction fees) [5](#0-4) , and by Substrate's own transaction-pool size limits, which cap how many transactions can be simultaneously "ready." However, distinct arbitrary `commitment` values are free to fabricate, and the watcher applies no dedup/rate control on the RPC-side cache independent of pool churn, so an attacker cycling nonces/fillers over the TTL window can sustain elevated memory use well beyond organic bid volume.

### Recommendation
Bound `BidCache` explicitly: cap total entries/bytes (e.g., LRU eviction or a hard per-`(commitment)`/global ceiling), reject/ignore cache inserts for fabricated commitments that don't correspond to a currently-active order (cross-check against `CurrentPhantomOrder`/known live orders before caching), and consider shortening `cleanup_interval` or triggering eviction proactively on insert (checking size before insert) rather than relying solely on a fixed-interval timer.

### Proof of Concept
1. Fund N accounts with the minimal deposit `storage_deposit_fee()`.
2. From each account, submit distinct `place_bid(commitment_i, user_op_i)` extrinsics with `user_op_i` sized near the 1MB `BoundedVec` cap and `commitment_i` set to arbitrary random `H256` values (no real order needs to exist).
3. Because `run_bid_watcher` caches on `import_notification_stream`/`ready_transaction` before inclusion [2](#0-1) , each transaction adds ~1MB to the process-resident `BidCache` regardless of whether it is later included or reverted.
4. Repeat continuously faster than the `cleanup_interval` TTL to keep memory usage climbing until the RPC/collator node exhausts available memory.

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

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L373-377)
```rust
			_ = timer.tick() => {
				if let Err(e) = bid_cache.remove_expired() {
					log::warn!(target: LOG_TARGET, "failed to clean bid cache: {e}");
				}
			}
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L323-343)
```rust
		/// Place a bid for an order
		///
		/// # Parameters
		/// - `commitment`: The order commitment hash
		/// - `user_op`: The signed user operation as opaque bytes (max 1MB)
		///
		/// # Errors
		/// - `InsufficientBalance`: If the filler doesn't have enough balance for the deposit
		/// - `InvalidUserOp`: If the user operation data is invalid or exceeds 1MB
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

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L360-370)
```rust

			// If a bid already exists, unreserve the old deposit first
			if let Some(old_deposit) = Bids::<T>::get(&commitment, &filler) {
				<T as Config>::Currency::unreserve(&filler, old_deposit);
			}

			let deposit = Self::storage_deposit_fee();

			// Reserve the new deposit
			<T as Config>::Currency::reserve(&filler, deposit)
				.map_err(|_| Error::<T>::InsufficientBalance)?;
```
