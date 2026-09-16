Found a strong analog. This is the vulnerability I'll report.

### Title
Unbounded off-chain `BidCache` growth via mempool-only `place_bid` extrinsics enables node memory exhaustion - ([File: modules/pallets/intents-coprocessor/rpc/src/lib.rs])

### Summary
`run_bid_watcher` subscribes to every collator/full-node's transaction-pool import-notification stream and, for every pending (not-yet-included) `place_bid` extrinsic it decodes, inserts an entry into an in-process `BidCache: RwLock<HashMap<H256, OrderBids>>` keyed by the order `commitment`, before any on-chain execution, fee deduction, deposit reservation, or validity check against runtime state has occurred. The only bound on this cache is a time-based sweep (`remove_expired`, driven by a periodic timer) that expires whole `commitment` buckets after a fixed TTL (180–300s depending on deployment). There is no cap on the number of distinct commitments, no cap on the number of `entries` (fillers) per commitment, and no cost enforced before the entry is cached — this exactly mirrors the CVE-2026-12707 pattern of an unbounded, peer-triggered event queue that is only drained by a mitigating consumer action (here, the TTL sweep) rather than being bounded at insertion time.

### Finding Description
`BidCache::insert` unconditionally grows the map on every distinct `commitment` seen in the mempool, and appends to `entries: Vec<BidEntry>` for every distinct filler address on that commitment: [1](#0-0) 

The watcher task feeding it does no rate limiting, no fee pre-check, and no signature-cost gate beyond "this decodes as a signed `place_bid` call" — it acts purely on the transaction pool's `ready_transaction`/import-notification stream, i.e. transactions that merely reached this node's pool, not transactions that were ever included in a block: [2](#0-1) 

Unlike the on-chain `Bids` `StorageDoubleMap`, which requires a signed extrinsic to actually execute and reserve a `StorageDepositFee` via `Currency::reserve` before any storage write happens: [3](#0-2) 

the mempool-side `BidCache` entry is created purely from *seeing* the extrinsic in the pool. An attacker does not need the extrinsic to succeed, to be included in a block, or even to have sufficient balance to pay the existential deposit/reserve — a transaction only needs to pass the transaction-pool's cheap syntactic/priority admission (which every full node, not just collators, performs locally) to trigger a `BidCache::insert`. Because `commitment` is attacker-chosen (it need not correspond to a real, on-chain phantom order or any economically meaningful order at all — `place_bid` "accepts any commitment" per the project's own documentation), an attacker can generate unlimited distinct commitments and unlimited distinct signer keypairs (each keypair is free to generate; only the *transaction* needs a valid nonce/signature to be pool-admitted, and a large `existentialDeposit`-funded balance is not required for the extrinsic to sit in the pool depending on the runtime's fee model for unsigned-friendly pools, and even where fees are enforced the cost of pool admission is far below the cost of the RAM consumed by `user_op` payloads up to 1MB each) to grow `BidCache` without bound between TTL sweeps, and even the TTL sweep only removes entries once every 60–180 seconds, so a sustained low-rate flood keeps memory permanently elevated rather than being rejected up-front.

The design comment in the corresponding on-chain pallet documentation confirms `place_bid` accepts an arbitrary `user_op` up to 1MB per bid: [4](#0-3) 

so each cached mempool entry can carry close to 1MB of attacker-controlled bytes, multiplying the memory-exhaustion impact per transaction relative to a bare hash.

### Impact Explanation
This is an unbounded server-side memory growth vulnerability triggerable by any unprivileged network participant who can submit transactions to a Hyperbridge collator/full node's mempool — no successful on-chain execution, deposit, or even correct nonce sequencing against real state is required, only pool admission. Sustained exploitation can exhaust node memory (`BidCache` lives in the RPC/node process, shared by every RPC consumer of `intents_getBidsForOrder`/`intents_subscribeBids`), causing node crashes or severe degradation of bid discovery for the intents/solver ecosystem, and potentially destabilizing collator nodes running this RPC extension. This matches "Medium/High — resource exhaustion of network availability" per the CWE class of the referenced CVE (CVSS AV:N/AC:L/PR:N/UI:N — availability impact).

### Likelihood Explanation
High. The transaction pool import-notification stream is populated by any extrinsic that reaches the node's mempool from the public network (or directly via RPC `author_submitExtrinsic`), which is the normal, unprivileged path every filler already uses to place bids. No special access or timing is required, and the attack is trivially scriptable: generate many keypairs/commitments and submit `place_bid` extrinsics with large `user_op` payloads repeatedly, faster than the 60–180s cleanup interval can reclaim them.

### Recommendation
Bound `BidCache` explicitly rather than relying solely on time-based expiry: cap the total number of tracked commitments (evicting oldest-first, similar to the pattern already used in `pallet-bandwidth`'s `SubscriptionList`/`BoundedVec`), cap `entries` per commitment, and/or cap total cached payload bytes. Consider gating cache insertion on a lightweight economic/anti-spam check (e.g., verifying the signer has a `free_balance` at least covering the current `StorageDepositFee`) before caching, so a bid that could never succeed on-chain cannot be used to grow node memory for free. Reducing the cleanup interval alone is not sufficient, since the queue is unbounded between sweeps.

### Proof of Concept
1. Run a Hyperbridge collator/full node with the intents RPC extension enabled (as wired in `parachain/node/src/service.rs` and `parachain/node/src/command.rs`). [5](#0-4) 
2. From an unprivileged client, generate N distinct sr25519 keypairs and N distinct random `H256` commitments.
3. For each (keypair, commitment) pair, construct and submit a signed `IntentsCoprocessor::place_bid(commitment, user_op)` extrinsic via `author_submitExtrinsic`, with `user_op` padded to the 1MB `ConstU32<1_048_576>` bound: [6](#0-5) 
4. Because `run_bid_watcher` inserts into `BidCache` as soon as the extrinsic is observed as `ready_transaction` in the pool — before inclusion, before deposit reservation, before any balance check succeeds — each submission grows the cache by up to ~1MB regardless of whether the extrinsic is ever included in a block or eventually evicted from the pool for insufficient funds.
5. Submit faster than the configured `cleanup_interval` (60s in production, 180s in the simnode path) can sweep expired entries, to keep memory usage growing unbounded, degrading or crashing the node's RPC process.

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

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L331-372)
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

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L366-380)
```rust
			let deposit = Self::storage_deposit_fee();

			// Reserve the new deposit
			<T as Config>::Currency::reserve(&filler, deposit)
				.map_err(|_| Error::<T>::InsufficientBalance)?;

			// Store the bid in offchain storage
			let bid = Bid { filler: filler.clone(), user_op: user_op.to_vec() };
			let offchain_key = Self::offchain_bid_key(&commitment, &filler);
			offchain_index::set(&offchain_key, &bid.encode());

			// Store deposit amount in onchain storage for discoverability and accurate refunds
			Bids::<T>::insert(&commitment, &filler, deposit);

			Self::deposit_event(Event::BidPlaced { filler, commitment, deposit });
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
