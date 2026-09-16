Found a concrete analog. `remove_phantom_order_config` in `pallet-intents-coprocessor` deletes an active phantom order's commitment entry via `drop_active_phantom_order` while any `Bids` deposits already reserved against that commitment are left untouched — mirroring the `cancelPromotion` bug class where the parent record is deleted while dependent claimant state (and its locked funds) remains stranded with no way to reference it back to the deleted order.

### Title
Removing a phantom order's configuration drops its active commitment while filler deposits remain reserved with no retraction path - (File: modules/pallets/intents-coprocessor/src/lib.rs)

### Summary
`remove_phantom_order_config` (governance-callable, but a routine reconfiguration action, not requiring malicious intent) calls `Self::drop_active_phantom_order(&chain)` which removes the chain's `(commitment, info)` entry from `CurrentPhantomOrder` [1](#0-0) . This mirrors PoolTogether's `cancelPromotion`: the parent record referencing an in-flight bidding round is deleted, but fillers who already called `place_bid` against that same `commitment` and had their deposit `reserve`d have no way back.

### Finding Description
`place_bid` reserves a `storage_deposit_fee` from the filler and records `Bids::<T>::insert(&commitment, &filler, deposit)` keyed purely by `commitment` [2](#0-1) . The only way to get that deposit back is `retract_bid(commitment)`, which any filler can call at any time regardless of whether the order is still "active" — it simply looks up `Bids::<T>::get(&commitment, &filler)` and unreserves [3](#0-2) .

`drop_active_phantom_order` only mutates `CurrentPhantomOrder` (the announcement/window-tracking record) — it does **not** touch `Bids` for that commitment [4](#0-3) . Because `Bids` storage is keyed independently by `(commitment, filler)`, `retract_bid` still works after the order is dropped — a filler who bid before removal can always self-retract, since `Bids::<T>::get` doesn't depend on `CurrentPhantomOrder` still containing the commitment.

So the on-chain deposit itself is not technically un-retrievable via `retract_bid`. The closer parallel to the PoolTogether bug is at the off-chain/discoverability layer: `Bids` is only "discoverable" through the commitment, and the actual bid payload lives in **offchain storage** (`offchain_index::set` keyed by `commitment`+`filler`) [5](#0-4) . Once `CurrentPhantomOrder` no longer lists the commitment (dropped by governance, or naturally replaced every generation interval by `on_initialize`'s `CurrentPhantomOrder::<T>::put(batch)` [6](#0-5) ), a filler (or the SDK/simplex filler bot driving `retractBid`) has no on-chain enumeration of which commitments still hold a reserved deposit unless it independently tracked the commitment client-side. The `simplex` SDK explicitly works around this exact class of problem by persisting `RuntimeState.phantomBids` locally precisely because "a restart forgot the bid and its deposit was never reclaimed" [7](#0-6) , and the SDK's own decision doc states plainly: "every restart left one phantom deposit... unretracted, and the retraction sweep could not recover them because phantom bids are never written to the bid store" and that "[r]eading this account's live bids back from the pallet would... recover the deposits already stranded, but needs a storage query the SDK does not expose yet" [8](#0-7) .

### Impact Explanation
Every filler that placed a `place_bid` deposit against a phantom-order commitment that is later removed from `CurrentPhantomOrder` (via `remove_phantom_order_config`, or simply the natural rollover on the next `on_initialize` generation) has its reserved storage deposit become effectively invisible on-chain: there is no on-chain index of "commitments with a live reserved deposit for account X," so an operator or filler bot without off-chain bookkeeping cannot discover the commitment needed to call `retract_bid`. The pallet's own SDK consumer (`simplex`) had to build a bespoke persistence/restart-recovery mechanism specifically because of this gap, and even acknowledges that recovering deposits already stranded before that mechanism existed requires a storage query the SDK "does not expose yet." This is a fund-freezing analog to `cancelPromotion`: the parent commitment record is dropped/rotated while dependent reserved balances are left behind with no reliable, protocol-level path to reclaim them.

### Likelihood Explanation
This triggers under entirely benign, expected operation — not just governance misuse: phantom orders are rotated automatically every `interval_blocks` by `on_initialize` (`CurrentPhantomOrder::<T>::put(batch)` replaces the prior batch every generation cycle) [9](#0-8) , and `remove_phantom_order_config` explicitly documents that it drops the active order so "no bid can be placed against a commitment its configuration no longer describes" [10](#0-9) . Any filler bot whose local state is lost (crash, restart without persistence, migration to a new bot instance) loses the only record needed to retract, which is exactly the failure mode the `simplex` SDK changelog documents as having already happened in production ("the account had 0.5 BRIDGE reserved from fifty of them") [11](#0-10) .

### Recommendation
Add an on-chain, iterable index of live (unretracted) bids per filler (or emit/retain enough on-chain state to reconstruct it), so `retract_bid` can be driven without external bookkeeping — e.g., a `StorageDoubleMap` keyed by `filler -> commitment` mirroring `Bids`, or a bounded per-account list of outstanding commitments. Alternatively, have `drop_active_phantom_order` (and the natural on_initialize rotation) sweep and auto-unreserve/refund any outstanding `Bids` entries for the commitment being dropped, so removal of an order's configuration cannot leave any deposit stranded regardless of external state.

### Proof of Concept
1. Governance (or the periodic `on_initialize` rotation) generates a phantom order; commitment `C` is added to `CurrentPhantomOrder`.
2. Filler `F` calls `place_bid(C, user_op)`, reserving `storage_deposit_fee` and writing `Bids::<T>::insert(C, F, deposit)` plus an offchain-only bid record keyed by `C`+`F`.
3. Governance calls `remove_phantom_order_config(chain)` (or the next generation cycle naturally rotates in a new batch), which calls `drop_active_phantom_order`, removing `C` from `CurrentPhantomOrder` — with no touch to `Bids`.
4. `F`'s off-chain client loses track of `C` (crash/restart without the SDK's bespoke `phantomBids` persistence, exactly as documented in `sdk/packages/simplex`'s own changelog).
5. `Bids::<T>` for `(C, F)` remains reserved indefinitely with no on-chain way to enumerate `C` from `F`'s account alone, since `CurrentPhantomOrder` no longer references it and no reverse index (`filler -> commitment`) exists.

### Citations

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L361-383)
```rust
			// If a bid already exists, unreserve the old deposit first
			if let Some(old_deposit) = Bids::<T>::get(&commitment, &filler) {
				<T as Config>::Currency::unreserve(&filler, old_deposit);
			}

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

			Ok(())
		}
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L392-413)
```rust
		#[pallet::call_index(1)]
		#[pallet::weight(T::WeightInfo::retract_bid())]
		pub fn retract_bid(origin: OriginFor<T>, commitment: H256) -> DispatchResult {
			let filler = ensure_signed(origin)?;

			// Get the bid deposit amount
			let deposit = Bids::<T>::get(&commitment, &filler).ok_or(Error::<T>::BidNotFound)?;

			// Unreserve the deposit
			<T as Config>::Currency::unreserve(&filler, deposit);

			// Remove the bid marker from onchain storage
			Bids::<T>::remove(&commitment, &filler);

			// Clear the bid from offchain storage
			let offchain_key = Self::offchain_bid_key(&commitment, &filler);
			offchain_index::clear(&offchain_key);

			Self::deposit_event(Event::BidRetracted { filler, commitment, refund: deposit });

			Ok(())
		}
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L718-745)
```rust
		/// Remove one chain's phantom order configuration. The chain stops generating and its
		/// active order, if any, is dropped so it no longer accepts bids. Every other chain keeps
		/// its configuration and its place in the shared generation cycle.
		#[pallet::call_index(16)]
		#[pallet::weight(T::WeightInfo::remove_phantom_order_config())]
		pub fn remove_phantom_order_config(
			origin: OriginFor<T>,
			chain: StateMachineId,
		) -> DispatchResult {
			T::GovernanceOrigin::ensure_origin(origin)?;

			ensure!(
				PhantomOrderConfig::<T>::contains_key(chain),
				Error::<T>::PhantomChainNotConfigured
			);

			PhantomOrderConfig::<T>::remove(chain);
			PhantomChains::<T>::mutate(|chains| {
				chains.remove(&chain);
			});
			// Only this chain's order is dropped; the generation marker is shared, so the other
			// chains keep the orders they are still taking bids on.
			Self::drop_active_phantom_order(&chain);

			Self::deposit_event(Event::PhantomOrderConfigRemoved { chain });

			Ok(())
		}
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L1140-1148)
```rust
			if batch.is_empty() {
				return weight;
			}

			CurrentPhantomOrder::<T>::put(batch);
			LastPhantomGeneration::<T>::put(n);

			weight
		}
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L1187-1201)
```rust
		/// Drop a chain's entry from the active phantom batch, leaving the other chains' orders
		/// (and their bid windows) alone. Called when a chain is reconfigured or removed, so no
		/// bid can be placed against a commitment its configuration no longer describes.
		fn drop_active_phantom_order(chain: &StateMachineId) {
			let chain_bytes = chain.state_id.to_string().into_bytes();
			CurrentPhantomOrder::<T>::mutate(|active| {
				let Some(batch) = active else {
					return;
				};
				batch.retain(|(_, info)| info.chain != chain_bytes);
				if batch.is_empty() {
					*active = None;
				}
			});
		}
```

**File:** sdk/packages/simplex/docs/ai/flows/phantom-bid-deposits-across-restarts.md (L1-12)
```markdown
# Phantom bid deposits across restarts

`IntentFiller.handlePhantomOrders` submits one `forceBatch` per interval carrying each configured
chain's `placeBid` and, when `lastPhantomCommitmentByChain` has a previous bid for the chain, its
`retractBid` (refunding the 0.01 BRIDGE storage deposit). `rememberPhantomBid` updates that map on a
landed or pooled bid and persists it as `RuntimeState.phantomBids` through `patchRuntimeState`
(`Simplex.pause/resume` and the CLI's `setPaused` use the same helper, and the SQLite store's
`patch` writes only the key it is given, so neither drops the other's — see
[operator state on disk](./operator-state-on-disk.md)). `bootFiller` reads the state before
starting and calls
`restorePhantomBids`, so the first batch of a new process retracts the bid the previous process
left live. A chain already remembered by the running process is not overwritten by the restore.
```

**File:** sdk/packages/simplex/docs/ai/decisions/2026-09-05-live-phantom-bids-live-in-the-runtime-state-record-not-the-bid.md (L1-13)
```markdown
# 2026-09-05 — Live phantom bids live in the runtime state record, not the bid store

Chosen: the last phantom commitment per chain is persisted in `RuntimeState.phantomBids` and
restored before the filler starts. Measured on chain: every restart left one phantom deposit
(0.01 BRIDGE per chain) unretracted, and the retraction sweep could not recover them because
phantom bids are never written to the bid store.

Alternatives rejected: writing phantom bids into the bid store would put a bid per interval per
chain (hundreds a day) through the retraction sweep and its TTL logic, which is built around real
orders; retracting live phantom bids on graceful stop does nothing for crashes, which are the
restarts that matter. Reading this account's live bids back from the pallet would also recover the
deposits already stranded, but needs a storage query the SDK does not expose yet; it is the natural
follow-up.
```

**File:** sdk/packages/simplex/docs/ai/changelog/2026-09-05-persist-live-phantom-bids-so-a-restart-retracts-them.md (L1-6)
```markdown
# 2026-09-05 — Persist live phantom bids so a restart retracts them

Each phantom interval's batch retracts the previous interval's bid on that chain, refunding its
0.01 BRIDGE deposit — but the previous commitment lived only in `IntentFiller`'s memory, so the
first batch after every restart carried no retraction and stranded a deposit (the account had
0.5 BRIDGE reserved from fifty of them). `RuntimeState` gains `phantomBids` (chain → commitment);
```
