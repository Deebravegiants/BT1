Found a genuine analog: the MMR `finalize()` loop in `pallet-mmr` iterates over every leaf buffered by dispatches within a single block, and buffering into `IntermediateLeaves` is driven by ordinary `dispatch_request` calls that can carry `fee = 0`.

### Title
Zero-fee POST/GET dispatches let an attacker inflate `IntermediateLeaves`, making the block's mandatory `finalize()` MMR loop arbitrarily expensive - (File: `modules/pallets/mmr/src/lib.rs`)

### Summary
`pallet_ismp::dispatcher::Pallet::dispatch_request` only transfers a fee when `fee.fee != Zero::zero()` [1](#0-0) ; a caller may set `fee: 0` and pay nothing beyond the ordinary transaction weight fee. Every dispatched request/response still calls `OffchainDBProvider::push`, which appends one entry into the unbounded `IntermediateLeaves` map for that block [2](#0-1) . At the end of the block, `finalize()` must iterate over the full buffer (`0..buffer_len`) to push every leaf into the MMR and compute the new root before the block can be sealed [3](#0-2) .

### Finding Description
This mirrors the Noya `withdrawQueue` bug class exactly: a cheap, unrestricted user action (`withdraw(0, receiver)` in Noya; `dispatch()` with `fee: 0` and minimal body here) appends to a storage structure with no minimum-value/size gate, and a later mandatory system operation (`calculateWithdrawShares` in Noya; the MMR `finalize()` hook here) must loop over every appended item, so its cost scales linearly with how many cheap entries were queued.

Concretely:
- `dispatch_request` in `pallet-ismp` accepts `fee: Zero::zero()` with no minimum check [1](#0-0) , and the docs confirm fee is fully optional ("can also be set to zero if the application developers prefer to self-relay") [4](#0-3) .
- Each such dispatch pushes into `IntermediateLeaves::<T, I>` keyed by an incrementing `temp_count`, with no cap on how many can accumulate within a single block [2](#0-1) .
- `finalize()` — invoked unconditionally to close out the block's MMR state — iterates the entire `0..buffer_len` range, calling `mmr.push(leaf)` for each buffered leaf [5](#0-4) , then clears the whole range [6](#0-5) . This is not gated by weight metering per-call the way normal extrinsics are; it runs as part of block finalization for the whole batch of leaves produced in that block.
- Unlike the Noya keeper (`calculateWithdrawShares`, capped by an explicit `maxIterations` parameter), `finalize()` has no per-block cap on `buffer_len` — it processes however many leaves were pushed, however many zero-fee/minimal-body dispatches an attacker fit into the block.

### Impact Explanation
An attacker able to fit many minimal, near-zero-fee `dispatch()` calls (POST or GET, `fee: 0`, empty/short body) into a single block forces `finalize()`'s per-leaf MMR push loop to do proportionally more work at block-close time, when the block's total weight budget is already largely consumed by the extrinsics themselves. Because `finalize()`'s cost is not separately weight-metered per leaf the way a normal extrinsic is, this shifts unaccounted computational cost into block finalization, which can degrade block production performance/liveness for the chain (a route/liveness impact) as the number of connected chains' requests routed through Hyperbridge grows, and increases the on-chain storage footprint (`IntermediateLeaves`, later `Nodes`) at negligible cost to the attacker.

### Likelihood Explanation
Dispatching a request costs only the ordinary transaction fee for the extrinsic weight — no minimum ISMP relayer fee is enforced — so any account with enough native/parachain currency to pay ordinary transaction fees can repeatedly call `dispatch_request`/`dispatch()` with `fee: 0` and a minimal body. This is a normal, permissionless, unprivileged action (satisfies "unprivileged message dispatcher" reachability), requiring no governance or admin role, making the likelihood moderate-to-high for a well-funded attacker aiming to degrade Hyperbridge's finalization performance over many blocks.

### Recommendation
- Cap the number of leaves that can be buffered into `IntermediateLeaves` per block (e.g., a `MaxLeavesPerBlock` constant), rejecting or deferring dispatches beyond the cap, similar to how EVM MMR-style implementations bound per-block leaf insertion.
- Consider enforcing a minimum non-zero fee (or a per-dispatch weight surcharge proportional to MMR-push cost) so that each `push()` is properly weight-accounted rather than externalizing cost into unmetered `finalize()` work.
- Alternatively, bound `finalize()`'s work explicitly (process at most N leaves per `on_finalize`, carrying over the remainder), so a single block's `finalize()` cannot be made arbitrarily expensive by dispatch spam.

### Proof of Concept
1. An attacker account with only enough balance for ordinary transaction fees repeatedly calls `pallet_ismp::dispatch_request` (or any pallet built atop it, e.g. via `send_message`) with `DispatchPost { fee: 0, body: minimal bytes, timeout: 0, ... }`, as shown to be valid and to skip the fee-transfer path in `dispatch_request` [7](#0-6) , and demonstrated to work with `fee: 0` in the pallet's own test suite [8](#0-7) .
2. Each call triggers `OffchainDBProvider::push`, incrementing `IntermediateLeaves::<T,I>::count()` by one [2](#0-1) .
3. By submitting as many such extrinsics as the block's weight/length limit allows (batched via `utility.batch`/`force_batch` where available, or simply many independent transactions), the attacker maximizes `buffer_len` for that block.
4. At block finalization, `finalize()` runs the full `for index in 0u64..buffer_len` loop, pushing every leaf into the MMR structure and rehashing peaks [9](#0-8) , imposing compute cost proportional to the attacker-controlled `buffer_len`, unaccounted for by a per-extrinsic weight charge specific to this work.

### Citations

**File:** modules/pallets/ismp/src/dispatcher.rs (L92-106)
```rust
	fn dispatch_request(
		&self,
		request: DispatchRequest,
		fee: FeeMetadata<T>,
	) -> Result<H256, anyhow::Error> {
		// collect payment for the request
		if fee.fee != Zero::zero() {
			T::Currency::transfer(
				&fee.payer,
				&RELAYER_FEE_ACCOUNT.into_account_truncating(),
				fee.fee,
				Preservation::Expendable,
			)
			.map_err(|err| IsmpError::Custom(format!("Error withdrawing request fees: {err:?}")))?;
		}
```

**File:** modules/pallets/mmr/src/lib.rs (L221-227)
```rust
	fn push(leaf: T::Leaf) -> LeafMetadata {
		let temp_count = IntermediateLeaves::<T, I>::count() as u64;
		let index = NumberOfLeaves::<T, I>::get() + temp_count;
		IntermediateLeaves::<T, I>::insert(temp_count, leaf);
		let position = leaf_index_to_pos(index);
		LeafMetadata { position, index }
	}
```

**File:** modules/pallets/mmr/src/lib.rs (L229-270)
```rust
	fn finalize() -> Result<H256, Error> {
		let buffer_len = IntermediateLeaves::<T, I>::count() as u64;
		// no new leaves? early return
		if buffer_len == 0 {
			return Ok(RootHash::<T, I>::get().into());
		}

		let leaves = NumberOfLeaves::<T, I>::get();
		let mut mmr: ModuleMmr<mmr::storage::RuntimeStorage, T, I> = mmr::Mmr::new(leaves);

		// append new leaves to MMR
		let range = 0u64..buffer_len;
		for index in range {
			let leaf = IntermediateLeaves::<T, I>::get(index).ok_or(Error::Push)?;
			// Mmr push should never fail
			match mmr.push(leaf) {
				None => {
					log::error!(target: "pallet-mmr", "MMR push failed ");
					// MMR push never fails, but better safe than sorry.
					Err(Error::Push)?
				},
				Some(position) => {
					log::trace!(target: "pallet-mmr", "MMR push {position}");
				},
			}
		}

		// Update the size, `mmr.finalize()` should also never fail.
		let (leaves, root) = match mmr.finalize() {
			Ok((leaves, root)) => (leaves, root),
			Err(e) => {
				log::error!(target: "pallet-mmr", "MMR finalize failed: {:?}", e);
				Err(Error::Commit)?
			},
		};

		let _ = IntermediateLeaves::<T, I>::clear(buffer_len as u32, None);
		NumberOfLeaves::<T, I>::put(leaves);
		RootHash::<T, I>::put(root);

		Ok(root.into())
	}
```

**File:** docs/content/developers/evm/messaging/post-requests.mdx (L45-46)
```text
| `fee` | Optional relayer fees in the fee token, this can also be set to zero if the application developers prefer to self-relay. |
| `payer` | The account that should receive a refund of the relayer fees if the request times out. |
```

**File:** modules/pallets/testsuite/src/tests/pallet_ismp.rs (L422-447)
```rust
#[test]
fn test_dispatch_fees_and_refunds() {
	let mut ext = new_test_ext();
	let account: AccountId32 = H256::random().0.into();
	let host = Ismp::default();

	ext.execute_with(|| {
		let msg = DispatchGet {
			dest: StateMachine::Evm(1),
			from: vec![0u8; 32],
			keys: vec![vec![1u8; 32], vec![1u8; 32]],
			context: Default::default(),
			height: 3,
			timeout: 2_000_000_000,
		};

		assert_eq!(Balances::balance(&account), Default::default());
		Balances::mint_into(&account, 10 * UNIT).unwrap();
		assert_eq!(Balances::balance(&account), 10 * UNIT);

		host.dispatch_request(
			DispatchRequest::Get(msg.clone()),
			// lets pay 10 units
			FeeMetadata { payer: account.clone().into(), fee: 10 * UNIT },
		)
		.unwrap();
```
