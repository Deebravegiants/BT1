### Title
`place_bid`'s fixed weight and flat storage deposit let a filler post near-1MB `user_op` blobs at trivial cost, enabling cheap storage bloat that stalls order fulfillment - (File: `modules/pallets/intents-coprocessor/src/lib.rs`, `modules/pallets/intents-coprocessor/src/weights.rs`)

### Summary
The `pallet-intents-coprocessor::place_bid` extrinsic accepts a `user_op: BoundedVec<u8, ConstU32<1_048_576>>` (up to 1 MiB) [1](#0-0) , but the extrinsic's weight is a flat constant that is benchmarked against a 100-byte payload and does not scale with the actual size of `user_op` [2](#0-1) . Combined with a fixed `storage_deposit_fee()` reservation that also does not scale with payload size [3](#0-2) , any unprivileged filler can submit maximum-size (~1 MiB) bids for the fixed weight/fee price, mirroring the reported `_metadataURI` unbounded-length DoS/gas-inflation class.

### Finding Description
`Bid<AccountId>` stores `user_op` as a raw `Vec<u8>` decoded from the bounded input [4](#0-3) . The dispatchable is weighted with `SubstrateWeight::place_bid()`, which returns a hard-coded `Weight::from_parts(50_000_000, 0)` plus a fixed proof size term (`3000`), independent of the length of `user_op` [2](#0-1) . The benchmark that generated this weight only exercises a 100-byte `user_op` [5](#0-4) , so the weight/fee charged to the caller does not reflect the true cost of decoding, validating (`IsSubType` extraction, `DecodeWithMemTracking`), storing, and later re-encoding/transmitting a near-1MiB blob.

Because `place_bid` lets a filler overwrite their own bid on the same commitment repeatedly at this same flat cost [6](#0-5) , and every downstream consumer of `Bids` storage — the RPC path that extracts and decodes bids from extrinsics (`extract_bid`) [7](#0-6) , the indexer's `FillerBid` entity storing the raw SCALE-encoded payload [8](#0-7) , and the SDK's `decodeBid`/phantom-order price-snapshot aggregation that iterates all live bids for a commitment to select solvers [9](#0-8)  — must decode and process every filler's blob, an attacker can cheaply flood a commitment (or many commitments) with maximum-size bids to inflate the on-chain state, extrinsic pool bandwidth, and off-chain relayer/solver compute needed to enumerate and select a bid before the phantom bid window closes.

### Impact Explanation
Because solver selection for phantom/intents orders depends on enumerating and decoding all bids for a commitment within a bounded bid window before the order expires, cheaply flooding that window with maximum-size, underpriced bids can delay or prevent timely solver selection, risking that legitimate orders miss their fill window. Since intents lock user funds in escrow pending fulfillment, a stalled/failed selection process can leave user funds stuck until expiry/refund logic runs, which is a funds-availability (temporary freezing) impact reachable by any unprivileged filler with a normal Substrate account and minimal balance for the deposit.

### Likelihood Explanation
Likelihood is moderate: the attack requires only a signed account and enough balance for `storage_deposit_fee()` (a fixed amount per the benchmark) [3](#0-2) , no special privilege, and the bounded-vec size cap of ~1 MiB is generous enough to make each submission meaningfully larger and more expensive to process off-chain/downstream than the flat weight/fee suggests. This is an economically rational spam vector for any actor wishing to disrupt competing solvers or slow selection on high-value orders.

### Recommendation
Make `place_bid`'s weight (and ideally the reserved storage deposit) a function of `user_op.len()`, e.g. `Weight::from_parts(base, 0).saturating_add(per_byte_weight.saturating_mul(user_op.len() as u64))`, following the same pattern already used for `set_phantom_order_config(c)` and `generate_phantom_order(p)` which scale with an input-size parameter [10](#0-9) . Additionally consider lowering the practical `user_op` bound (1 MiB is far larger than any real `PackedUserOperation` needs, which typically only needs `callData`/`paymasterAndData` reasonably sized) and/or scaling the storage deposit with payload length so oversized bids are economically disincentivized.

### Proof of Concept
1. An attacker account with a signed key and the fixed `storage_deposit_fee()` balance calls `Intents::place_bid(origin, commitment, user_op)` where `user_op` is a `BoundedVec` filled to its 1,048,576-byte cap (well beyond any legitimate `PackedUserOperation` encoding) [1](#0-0) .
2. The extrinsic is charged the flat weight from `SubstrateWeight::place_bid()` (`50_000_000` + fixed `3000` proof size) regardless of the 1 MiB payload [2](#0-1) .
3. The attacker repeats this for many commitments/fillers (or repeatedly overwrites the same bid, which is allowed and re-uses the same deposit) [6](#0-5) , inflating `Bids` storage and the volume of data that RPC extraction, indexers, and solver-selection tooling must decode per commitment before the phantom bid window closes, at a cost far below the true processing burden imposed on the network.

### Citations

**File:** modules/pallets/intents-coprocessor/src/benchmarking.rs (L40-57)
```rust
	#[benchmark]
	fn place_bid() {
		let caller: T::AccountId = whitelisted_caller();
		let commitment = H256::repeat_byte(0xff);
		let user_op: BoundedVec<u8, ConstU32<1_048_576>> =
			vec![1u8; 100].try_into().expect("user_op fits in bounds");

		// Fund the caller
		let deposit = Pallet::<T>::storage_deposit_fee();
		let balance = deposit * 10u32.into();
		<T as Config>::Currency::make_free_balance_be(&caller, balance);

		#[extrinsic_call]
		_(RawOrigin::Signed(caller.clone()), commitment, user_op);

		// Verify bid was placed
		assert!(Bids::<T>::contains_key(&commitment, &caller));
	}
```

**File:** modules/pallets/intents-coprocessor/src/weights.rs (L64-72)
```rust
impl<T: frame_system::Config> WeightInfo for SubstrateWeight<T> {
	/// Storage: Bids (r:1 w:1)
	/// Proof Skipped: Bids (max_values: None, max_size: None, mode: Measured)
	fn place_bid() -> Weight {
		Weight::from_parts(50_000_000, 0)
			.saturating_add(Weight::from_parts(0, 3000))
			.saturating_add(T::DbWeight::get().reads(1))
			.saturating_add(T::DbWeight::get().writes(1))
	}
```

**File:** modules/pallets/intents-coprocessor/src/weights.rs (L128-136)
```rust
	fn set_phantom_order_config(c: u32) -> Weight {
		// The per-chain term covers validating one more chain's pairs and writing its entry.
		Weight::from_parts(20_000_000, 0)
			.saturating_add(Weight::from_parts(4_000_000, 0).saturating_mul(c.into()))
			.saturating_add(Weight::from_parts(0, 1_024))
			.saturating_add(T::DbWeight::get().reads(1))
			.saturating_add(T::DbWeight::get().writes(4))
			.saturating_add(T::DbWeight::get().writes(c.into()))
	}
```

**File:** modules/pallets/intents-coprocessor/src/types.rs (L296-303)
```rust
/// A bid placed by a filler for an order
#[derive(Clone, Debug, Encode, Decode, DecodeWithMemTracking, TypeInfo, PartialEq, Eq)]
pub struct Bid<AccountId> {
	/// The filler who placed this bid
	pub filler: AccountId,
	/// The signed user operation (opaque bytes)
	pub user_op: Vec<u8>,
}
```

**File:** modules/pallets/intents-coprocessor/src/tests.rs (L209-238)
```rust
#[test]
fn filler_can_update_own_bid() {
	new_test_ext().execute_with(|| {
		let filler = AccountId32::new([1; 32]);
		let commitment = H256::random();
		let user_op_1 = BoundedVec::try_from(vec![1u8, 2u8, 3u8]).unwrap();
		let user_op_2 = BoundedVec::try_from(vec![4u8, 5u8, 6u8]).unwrap();

		// Place first bid
		assert_ok!(Intents::place_bid(
			RuntimeOrigin::signed(filler.clone()),
			commitment,
			user_op_1.clone()
		));

		// Verify bid exists
		assert!(Bids::<Test>::contains_key(&commitment, &filler));
		assert_eq!(Balances::reserved_balance(&filler), Intents::storage_deposit_fee());

		// Update the bid with new user_op
		assert_ok!(Intents::place_bid(
			RuntimeOrigin::signed(filler.clone()),
			commitment,
			user_op_2.clone()
		));

		// Verify bid still exists and deposit is still reserved (only once)
		assert!(Bids::<Test>::contains_key(&commitment, &filler));
		assert_eq!(Balances::reserved_balance(&filler), Intents::storage_deposit_fee());
	});
```

**File:** modules/pallets/intents-coprocessor/rpc/src/lib.rs (L291-324)
```rust
/// Extract a bid from encoded extrinsic bytes using generic runtime types.
///
/// Decodes the extrinsic and uses `IsSubType` to extract the pallet-level
/// `place_bid` call, returning `(commitment, filler_encoded, user_op)`.
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

**File:** sdk/packages/indexer/src/configs/schema.graphql (L2296-2308)
```text
	commitment: String! @index

	"""
	SS58 address of the filler that placed the bid.
	"""
	filler: String! @index

	"""
	The raw bid payload — the SCALE-encoded PackedUserOperation the filler submitted, as hex. Stored
	undecoded so a bid stays fully re-interpretable as the fill ABI evolves, and because the pallet's
	own copy expires. Null when neither the extrinsic nor the RPC yielded it.
	"""
	bidData: String
```

**File:** sdk/packages/sdk/src/chains/intentsCoprocessor.ts (L1151-1161)
```typescript
	/** Decodes SCALE-encoded Bid struct and SCALE-encoded PackedUserOperation */
	private decodeBid(hex: HexString): { filler: string; userOp: PackedUserOperation } {
		const decoded = BidCodec.dec(hexToU8a(hex))
		const filler = new Keyring({ type: "sr25519" }).encodeAddress(new Uint8Array(decoded.filler))
		const userOpHex = u8aToHex(new Uint8Array(decoded.user_op)) as HexString

		// Decode UserOp using SCALE codec
		const userOp = decodeUserOpScale(userOpHex)

		return { filler, userOp }
	}
```
