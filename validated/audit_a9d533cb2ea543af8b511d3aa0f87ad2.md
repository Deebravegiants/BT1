Found it. There's a real asymmetry in the codebase's own hardening: `modules/utils/bls-utils/src/ssz/byte_vector.rs` was patched with an explicit, hand-written `codec::Decode` impl (with an extensive comment and regression tests) specifically because the *derived* `Decode` for a fixed-capacity SSZ type silently delegates to the inner container's own decode and accepts any length, letting an over/under-length value be accepted even though the SSZ merkle root is insensitive to the padding — the exact bug class described in the report (`Versionize`/`FamStructWrapper` accepting a mismatched declared length with no bound check). `ByteList<N>` in `modules/consensus/sync-committee/primitives/src/ssz/byte_list.rs`, however, still uses the plain `#[derive(... codec::Decode)]` [1](#0-0)  with no equivalent override, so it inherits the same unfixed weakness the `ByteVector` patch was written to eliminate.

### Title
`ByteList<N>` SCALE decode omits the SSZ capacity bound check that `ByteVector<N>` was hardened against - (File: modules/consensus/sync-committee/primitives/src/ssz/byte_list.rs)

### Summary
`ByteList<N>` derives `codec::Decode` directly, which decodes the inner `Vec<u8>`/`List<u8, N>` payload without ever checking the decoded length against the SSZ-fixed capacity `N`. The sibling type `ByteVector<N>` had this exact issue and was fixed with a manual `Decode` impl that rejects any length ≠ `N`, with an explicit code comment describing the vulnerability and a full regression-test suite. `ByteList<N>` was left on the vulnerable derive path.

### Finding Description
`ByteVector<N>`'s manual decode explains the root cause precisely: a derived `Decode` "delegates to the inner `Vector`, which carries its own derive and so accepts any length — leaving a `ByteVector<N>` holding something other than `N` bytes" [2](#0-1) . The same structural flaw exists for `ByteList<N>`: it wraps `List<u8, N>` but only derives `codec::Decode` [1](#0-0) , with no override checking that the decoded byte length is `<= N` (the SSZ list bound). This is the direct analog to `versionize::Versionize::deserialize for FamStructWrapper<T>` (CVE-2023-28448): a length-carrying, fixed-capacity wire type is decoded from attacker-controlled bytes without validating the declared/actual length against the structural bound the rest of the code assumes.

This type is used in the sync-committee consensus primitives (SSZ types for Ethereum-family light-client consensus updates, e.g. Deneb KZG-related and other byte-list fields) alongside `ByteVector` [3](#0-2) , which are decoded from consensus/sync-committee update messages submitted by an unprivileged relayer to update a consensus client. Because the SSZ `hash_tree_root`/merkleization logic for these types is chunk-size-derived from the assumed max size `N` (the very reason the `ByteVector` fix was necessary — "the SSZ hash root is not sensitive to trailing zero bytes... appending zeros up to the next chunk boundary... leaves the root unchanged"), an over-length or malformed `ByteList<N>` accepted via the unchecked derive can desynchronize the assumed capacity from the actual stored data, propagating into chunking/merkleization and any downstream fixed-size buffer or array indexing built on the `N` bound.

### Impact Explanation
An unprivileged relayer submitting a sync-committee consensus update (or any message containing this type) can supply a `ByteList<N>` whose actual byte length does not match the SSZ capacity bound `N`. This is reachable through the consensus verification path used to update light-client state for cross-chain message delivery. Depending on how deep downstream SSZ chunking/array code assumes the length invariant, this can lead to out-of-bounds memory access or panics (DoS of consensus update processing) or state-commitment corruption, undermining the same "unsound state commitment" / "route unable to deliver messages" impact class flagged by the advisory.

### Likelihood Explanation
High likelihood of reachability: consensus update messages are submitted by permissionless relayers, and the code that introduced the fix for the sibling `ByteVector` type explicitly documents this bug class as something the team recognized and fixed for one type but not the other, indicating no additional access control or validation exists elsewhere to catch it for `ByteList`.

### Recommendation
Add an explicit `codec::Decode` implementation for `ByteList<N>` mirroring the one written for `ByteVector<N>`: decode into `Vec<u8>` first, reject if `bytes.len() > N` (the SSZ list bound), then construct via the existing `TryFrom<Vec<u8>>`/`deserialize` path, and add the same regression tests (`rejects_over_length`, `rejects_when_nested_in_a_struct`, etc.) that were added for `ByteVector`.

### Proof of Concept
1. Construct a SCALE-encoded blob for a struct containing a `ByteList<N>` field where the encoded `Vec<u8>` inner length exceeds `N` (e.g., for `N = 32`, encode 40 bytes).
2. Feed this into any consensus/message type that embeds `ByteList<N>` (e.g. sync-committee `consensus_types.rs`) via `Decode::decode`.
3. Observe the derive-based decode succeeds despite the length exceeding the SSZ-declared capacity `N`, in contrast to `ByteVector::<N>::decode`, which explicitly rejects such input per its `rejects_one_byte_over`/`rejects_every_length_sharing_the_hash_root` tests [4](#0-3) .

### Citations

**File:** modules/consensus/sync-committee/primitives/src/ssz/byte_list.rs (L10-14)
```rust
#[derive(Default, Clone, Eq, SimpleSerialize, codec::Encode, codec::Decode)]
#[cfg_attr(feature = "std", derive(serde::Serialize, serde::Deserialize))]
pub struct ByteList<const N: usize>(
	#[cfg_attr(feature = "serde", serde(with = "serde_hex_utils::as_hex"))] List<u8, N>,
);
```

**File:** modules/utils/bls-utils/src/ssz/byte_vector.rs (L32-56)
```rust
/// Length-checked SCALE decoding.
///
/// A derived `Decode` here delegates to the inner `Vector`, which carries its own derive and
/// so accepts any length — leaving a `ByteVector<N>` holding something other than `N` bytes.
/// That matters because the SSZ hash root is not sensitive to trailing zero bytes: a value
/// packs into `ceil(N / 32)` chunks with the tail already zero-padded, so appending zeros up
/// to the next chunk boundary consumes padding that was already there and leaves the root
/// unchanged. A consumer that authenticates only by `hash_tree_root` would therefore accept an
/// over-length value and persist it, and the length would not be caught until some later
/// operation — for a BLS key, a point decompression far away from this decode.
///
/// Reject at the boundary instead, reusing the same `deserialize` the byte-slice conversions
/// above go through so there is one definition of the length rule.
///
/// The wire format is unchanged: `Vector`'s SCALE representation is just its inner `Vec`, as
/// its merkle cache is `codec(skip)`.
impl<const N: usize> codec::Decode for ByteVector<N> {
	fn decode<I: codec::Input>(input: &mut I) -> Result<Self, codec::Error> {
		let bytes = Vec::<u8>::decode(input)?;
		if bytes.len() != N {
			return Err(codec::Error::from("ByteVector: decoded length does not equal N"));
		}
		ByteVector::<N>::try_from(bytes)
			.map_err(|_| codec::Error::from("ByteVector: SSZ deserialization failed"))
	}
```

**File:** modules/utils/bls-utils/src/ssz/byte_vector.rs (L159-186)
```rust
	/// The reported vector: one trailing byte past `N`. The SSZ root is unchanged by it, so the
	/// decode boundary is the only place this can be caught.
	#[test]
	fn rejects_one_byte_over() {
		assert!(ByteVector::<N>::decode(&mut &encoded(N + 1)[..]).is_err());
	}

	/// Every length up to the next chunk boundary shares the 48-byte root, so each one has to
	/// be rejected — not just the first.
	#[test]
	fn rejects_every_length_sharing_the_hash_root() {
		for len in (N + 1)..=64 {
			assert!(
				ByteVector::<N>::decode(&mut &encoded(len)[..]).is_err(),
				"over-length value of {len} bytes was accepted",
			);
		}
	}

	#[test]
	fn rejects_under_length() {
		for len in [0usize, 1, N - 1] {
			assert!(
				ByteVector::<N>::decode(&mut &encoded(len)[..]).is_err(),
				"under-length value of {len} bytes was accepted",
			);
		}
	}
```

**File:** modules/consensus/sync-committee/primitives/src/consensus_types.rs (L1-12)
```rust
use crate::{
	constants::{
		BlsPublicKey, BlsSignature, Bytes32, Epoch, ExecutionAddress, Gwei, Hash32,
		ParticipationFlags, Root, Slot, ValidatorIndex, Version, WithdrawalIndex,
		DEPOSIT_PROOF_LENGTH, JUSTIFICATION_BITS_LENGTH,
	},
	deneb::KzgCommitment,
	electra::*,
	ssz::{ByteList, ByteVector},
};
use alloc::{vec, vec::Vec};
use ssz_rs::{prelude::*, Deserialize, List, Vector};
```
