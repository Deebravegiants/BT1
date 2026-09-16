## Title
Phantom-order round rollover strands filler bid deposits without documented recovery - (File: modules/pallets/intents-coprocessor/src/lib.rs)

### Summary
The phantom-order subsystem in `pallet-intents-coprocessor` generates a new bundled order per configured chain every `interval_blocks` and stores it in `CurrentPhantomOrder`, replacing whatever commitment was active before [1](#0-0) . This is structurally the same "round overwritten, prior round's claims become orphaned" pattern described in the external report: a bounded, stateful auction round (Merkle distribution round ↔ phantom order round) is superseded by a new round, and participants whose stake belongs to the superseded round have no protocol-guaranteed path to recover it once the round is gone from the "current" pointer.

### Finding Description
`place_bid` enforces phantom-specific rules only against the order found in `CurrentPhantomOrder::<T>::get()` [2](#0-1) : the bid window check and one-bid-per-filler check are only evaluated for the commitment that is still the *active* entry in that storage item. Once `on_initialize`/the interval hook regenerates the phantom orders and overwrites `CurrentPhantomOrder` with the new interval's commitments (confirmed by the test `on_initialize replaces the commitment on each interval`, which shows a fresh commitment fully replacing the previous one every interval) [3](#0-2) , the old commitment is no longer discoverable through that map, even though:

- `Bids::<T>` entries for the old commitment remain in on-chain storage, keyed by `(commitment, filler)` [4](#0-3) .
- The filler's deposit remains `reserve()`d against their account, only released by an explicit `retract_bid(commitment)` call [5](#0-4) .

This mirrors the report's core defect exactly: a "round" pointer (`MerkleTrees`/`CurrentPhantomOrder`) is a single active slot, not a versioned map, so once it's overwritten there's no guaranteed on-chain accounting that reconciles the superseded round's outstanding claims/deposits. The off-chain filler (`simplex`) tries to compensate by remembering `lastPhantomCommitmentByChain` and manually submitting a `retractBid` for the just-replaced commitment on the next interval's batch [6](#0-5) , and documented incidents show this off-chain bookkeeping is fragile: a process restart without persisted state, a `BatchInterrupted` failure, or any other loss of `lastPhantomCommitmentByChain` strands the 0.01 BRIDGE deposit on-chain with no way for the pallet itself to reconcile it back, because the pallet has already forgotten which commitment was "the previous round" the instant `CurrentPhantomOrder` was overwritten [7](#0-6) . The retraction relies entirely on the filler independently remembering the exact `commitment` hash of the superseded round; the pallet exposes no "list of my open/expired bids" the filler (or a new operator) can query to recover from an unknown state.

### Impact Explanation
Every phantom-order interval that elapses permanently retires the previous round's commitment from `CurrentPhantomOrder` with no on-chain enumeration of outstanding bids tied to it. Any filler bid whose off-chain retraction bookkeeping is lost (crash before persistence, `BatchInterrupted`, wiped local state, or simply an operator that never captured the commitment) has its BRIDGE deposit permanently reserved with no discoverable path to recall it, since the commitment is not derivable from any current on-chain state once superseded — the filler must have independently recorded the exact `H256` commitment beforehand. This is a freezing-of-funds condition scoped to filler deposits (0.01 BRIDGE per stuck bid as documented), which compounds per missed interval across every configured chain pair.

### Likelihood Explanation
This is not a theoretical edge case — it has already manifested in production-adjacent operation: the SDK's own changelog documents that "every restart left one phantom deposit (0.01 BRIDGE per chain) unretracted, and the retraction sweep could not recover them because phantom bids are never written to the bid store" [8](#0-7) , and separately that a specific batching-order bug caused a "self-sustaining cascade" of stranded phantom deposits [9](#0-8) . Both fixes were applied entirely off-chain (persisting state, reordering the batch), because the pallet itself provides no on-chain recovery mechanism — confirming the root cause sits in the missing on-chain accounting for superseded rounds, exactly as the external report describes for the Merkle-distribution analog.

### Recommendation
Apply the same fix the external report recommends: don't rely on a single "current round" pointer as the sole means of tracking claimable state. Concretely:
- Expose a query/runtime API (or storage iteration) that lets a caller enumerate all `Bids` entries for a given `filler` account regardless of whether the associated commitment is still the "current" phantom order, so an operator can always discover and retract stale deposits without needing to have remembered the exact commitment off-chain.
- Alternatively, when `on_initialize` rotates `CurrentPhantomOrder`, have the pallet auto-unreserve/refund any bids still outstanding against the just-superseded commitment(s) as part of the rotation, closing the gap deterministically on-chain rather than depending on off-chain retraction.
- If the team decides the off-chain "remember and retract" pattern is acceptable, document explicitly (as the external report suggests) that filler deposits on superseded phantom rounds are only recoverable if the filler independently tracks and submits `retract_bid` against the exact stale commitment, and that no on-chain enumeration exists for recovery after state loss.

### Proof of Concept
1. Governance configures a phantom-order chain pair with a short `interval_blocks` via `set_phantom_order_config` [1](#0-0) .
2. `on_initialize` fires, generating commitment `C1` and inserting it into `CurrentPhantomOrder`.
3. A filler calls `place_bid(C1, user_op)`, reserving `storage_deposit_fee()` from their balance and inserting `Bids[C1][filler] = deposit` [10](#0-9) .
4. Before the filler (or its off-chain agent) submits `retract_bid(C1)`, the next interval elapses; `on_initialize` regenerates the phantom order set, and `CurrentPhantomOrder` is overwritten to point at `C2` (demonstrated by `on_initialize replaces the commitment on each interval`) [3](#0-2) .
5. `Bids[C1][filler]` still exists on-chain and the deposit is still reserved, but `C1` is no longer discoverable from `CurrentPhantomOrder`; the filler must already know `C1` (an opaque `H256`) to call `retract_bid(C1)` and reclaim funds.
6. If the filler's off-chain state that tracked `C1` is lost (crash, restart without persistence, a partially-failed batch — all documented incidents in `sdk/packages/simplex`), the deposit remains permanently reserved with no on-chain way to discover or recover it.

### Citations

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L347-359)
```rust
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
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L362-378)
```rust
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
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L392-412)
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
```

**File:** modules/pallets/intents-coprocessor/src/lib.rs (L612-625)
```rust
		/// Set the phantom order configuration for the chains the call carries, leaving every
		/// other configured chain's token pairs untouched. The on_initialize hook generates one
		/// bundled phantom order per configured chain when the interval elapses. Also clears the
		/// active orders and the generation marker so the hook fires on the next block.
		///
		/// `config.chains` is a map, so a call may configure a single chain or several at once,
		/// and a chain absent from it keeps whatever it already had — use
		/// [`remove_phantom_order_config`](Self::remove_phantom_order_config) to stop one.
		/// `config.interval_blocks` is the exception: it is shared by every configured chain, so
		/// all of them generate on the same block and their bid windows close together, and this
		/// call sets it for all of them.
		///
		/// Each configured pair is probed in BOTH directions — the generator expands it into a
		/// forward and a reverse leg — so a pair is registered once, not once per direction.
```

**File:** sdk/packages/simplex/src/tests/phantom-e2e.simnode.test.ts (L300-313)
```typescript
	it("on_initialize replaces the commitment on each interval", async () => {
		// interval_blocks=1 means the hook re-fires every block.
		await setPhantomOrderConfig(api, 8453, 1)

		await createBlock(api)
		const c1 = await getActivePhantomCommitment(api)
		expect(c1).not.toBeNull()

		await createBlock(api)
		const c2 = await getActivePhantomCommitment(api)
		expect(c2).not.toBeNull()

		expect(c1).not.toBe(c2)
	}, 60_000)
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

**File:** sdk/packages/simplex/docs/ai/changelog/2026-09-05-persist-live-phantom-bids-so-a-restart-retracts-them.md (L1-14)
```markdown
# 2026-09-05 — Persist live phantom bids so a restart retracts them

Each phantom interval's batch retracts the previous interval's bid on that chain, refunding its
0.01 BRIDGE deposit — but the previous commitment lived only in `IntentFiller`'s memory, so the
first batch after every restart carried no retraction and stranded a deposit (the account had
0.5 BRIDGE reserved from fifty of them). `RuntimeState` gains `phantomBids` (chain → commitment);
the filler takes a `StateStore` and persists the map whenever a phantom bid lands or is pooled
(`rememberPhantomBid`), boot seeds it with `restorePhantomBids(restoredState.phantomBids)` before
`start()`, and `livePhantomBids()` exposes it. `StateStore.set` replaces the whole record, so all
writers now go through `patchRuntimeState` (`src/data/state.ts`), including pause/resume in
`Simplex` and the CLI's `setPaused` — a pause no longer wipes the phantom bids. Added tests for
persistence, restore precedence and merge-safe pauses.
Files: `src/data/{state,types}.ts`, `src/core/{filler,boot}.ts`, `src/simplex.ts`,
`src/bin/simplex.ts`, `src/tests/phantom-bid-persistence.test.ts`, `docs/ai/{ChangeLog,Decisions,Flow}.md`.
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

**File:** sdk/packages/sdk/src/chains/intentsCoprocessor.ts (L911-924)
```typescript
	/**
	 * Places a new bid and retracts a previous one in a single transaction via utility.batch.
	 *
	 * The new bid is the primary operation, so `placeBid` MUST run first. `utility.batch` is
	 * non-atomic: a failing call interrupts the batch (via a BatchInterrupted event) without
	 * reverting the calls that already succeeded. Placing first guarantees the new bid lands even
	 * when the retraction then fails — which it routinely does, because a previous commitment's bid
	 * may already be gone (or was itself never placed), making `retractBid` return `BidNotFound`.
	 *
	 * Ordering retraction first (the previous behaviour) caused a self-sustaining cascade: a
	 * `BidNotFound` on the leading retract skipped the trailing `placeBid`, so the current bid never
	 * landed, so the *next* interval's retract of that never-placed commitment also failed, and so
	 * on — silently, because the batch extrinsic itself reports success. The deposit reclaim is
	 * best-effort; landing the bid is not.
```
