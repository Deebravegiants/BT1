### Title
Unbounded relayer-supplied `leaf_index` in BEEFY MMR leaf verification enables integer-overflow/panic DoS - (File: modules/consensus/beefy/verifier/src/lib.rs)

### Summary
`verify_mmr_leaf` in the BEEFY consensus verifier feeds an attacker/relayer-controlled `u64` (`mmr.mmr_proof.leaf_indices[0]`, taken verbatim from an unsigned, publicly submittable consensus message) directly into `leaf_index_to_mmr_size(leaf_index)` and `leaf_index_to_pos(leaf_index)` from the external `merkle-mountain-range` crate, with no upper-bound validation on the value.

### Finding Description
`verify_mmr_leaf` only checks that `leaf_indices.len() == 1` before extracting the value and passing it straight into position/size-computation helpers: [1](#0-0) 

This mirrors the CVE-2021-47432 bug class exactly: the Linux kernel's `generic-radix-tree.c::peek()` overflowed when computing an index/position from an unbounded, attacker-influenced numeric input near the type's maximum value. Here, `leaf_index_to_mmr_size` and `leaf_index_to_pos` perform bit-shift/arithmetic on `leaf_index` (an MMR "peek"-style position calculation) to derive the tree size and node position. Because `leaf_index` originates from the relayed/unsigned `ConsensusMessage` and is used before any sanity bound (e.g., versus the trusted state's current known height/leaf count), a crafted value close to `u64::MAX` can drive these arithmetic routines into overflow territory during `mmr_size`/`pos` computation.

This code path is reached from `verify_mmr_update_proof` → `verify_consensus`, which is the BEEFY `ConsensusClient::verify_consensus` entry point invoked from `pallet_ismp::handle_unsigned`, i.e. directly reachable by any unprivileged party submitting an unsigned consensus message/relayed proof — matching the required "message dispatcher / relayer / consensus verification" reachability class in the rules.

Notably, this exact function already has one recent hardening comment showing the team is aware `leaf_indices` is fully attacker-controlled and previously caused an unchecked-index panic: [2](#0-1) 

That fix only guarded the *length* of the vector, not the *magnitude* of the `u64` value inside it — the CVE-analog overflow surface in the size/position math remains unaddressed.

### Impact Explanation
If `leaf_index_to_mmr_size`/`leaf_index_to_pos` (or their internal peak/height helpers) perform unchecked arithmetic that overflows for values near `u64::MAX`, the effect depends on whether the runtime is compiled with overflow checks:
- If overflow checks are enabled, an attacker-crafted BEEFY consensus proof triggers a panic during `handle_unsigned` dispatch/validation — a runtime panic in a Substrate parachain node is a consensus-halting Denial of Service, unable to deliver any further ISMP messages (matches the "route unable to deliver messages" acceptance criterion).
- If overflow checks are disabled (release wraparound), the derived `mmr_size`/`leaf_pos` values wrap to small, attacker-chosen numbers. This could allow the `MmrMerkleProof::verify` call to be evaluated against an incorrect (attacker-favorable) proof structure, potentially enabling acceptance of a forged/invalid MMR leaf and unsound consensus state advancement — matching "unsound state commitment / forged message delivery".

I could not fully confirm from the indexed code whether the Hyperbridge parachain runtimes are built with `overflow-checks = true` (no `Cargo.toml` profile settings for this were found in the index), so the precise failure mode (hard panic vs. silent wraparound) is unconfirmed and would need to be validated by a background agent with full repo/build access.

### Likelihood Explanation
Medium. The path is reachable by any unprivileged actor submitting an unsigned `Message::Consensus` carrying a BEEFY `MmrProof` with an out-of-range `leaf_indices[0]` (e.g., near `u64::MAX`). It requires the BEEFY signature/authority-membership checks to have already been satisfied for a genuine authority set (the same precondition the existing empty-vector hardening comment discusses), or — depending on runtime wiring — could be gated by `IsmpCallFilter` on chains that route BEEFY exclusively through `pallet-beefy-consensus-proofs`'s SP1-verified path (as seen on `gargantua` and `nexus` runtimes): [3](#0-2) 

On any deployment where the naive/BEEFY `verify_mmr_update_proof` path (this `verifier/src/lib.rs`) is still reachable via `handle_unsigned` without such a filter, the likelihood of exploitation is higher since no signature over the leaf_index itself is needed to reach the vulnerable arithmetic — only a validly signed commitment, and the leaf_index field is not covered by any additional bound check.

### Recommendation
In `verify_mmr_leaf` (and any other call site that consumes relayer-supplied MMR `leaf_index`/`leaf_count` values), validate the numeric value before use:
- Reject `leaf_index` values that would make `mmr_size`/`pos` computations exceed reasonable/realistic bounds (e.g., compare against the trusted state's expected height-derived leaf count, or clamp to a sane maximum such as `u64::MAX / 2`).
- Use checked/saturating arithmetic (`checked_mul`, `checked_add`, etc.) around any custom position/size math introduced at the call site, and propagate an explicit `Error::InvalidMmrProof` rather than allowing a panic or silent wraparound.
- Add unit tests submitting a `leaf_index` near `u64::MAX` through `verify_mmr_leaf`/`verify_mmr_update_proof` to confirm graceful rejection.

### Proof of Concept
1. Construct a `ConsensusMessage` whose `mmr.signed_commitment` carries valid signatures from a known authority set (satisfying `check_participation_threshold`) and a legitimate 32-byte MMR root payload.
2. Set `mmr.mmr_proof.leaf_indices = vec![u64::MAX - 1]` (or another value chosen to trigger overflow in `leaf_index_to_mmr_size`/`leaf_index_to_pos`), with an arbitrary `mmr.mmr_proof.items` vector.
3. Submit this as an unsigned `Message::Consensus` via `pallet_ismp::Call::handle_unsigned` (or through `verify_consensus` directly in a test harness) on a runtime where the BEEFY naive verifier path is reachable.
4. Observe a panic (overflow-checked build) or an unexpected `mmr_size`/`leaf_pos` value being fed into `MmrMerkleProof::verify`, potentially producing an incorrect verification result (release build without overflow checks) — confirmable by tracing through `merkle_mountain_range::leaf_index_to_mmr_size`/`leaf_index_to_pos` with the crafted input in isolation.

### Citations

**File:** modules/consensus/beefy/verifier/src/lib.rs (L225-246)
```rust
fn verify_mmr_leaf<H: Keccak256 + Send + Sync>(
	mmr: &MmrProof,
	mmr_root: H256,
) -> Result<(), Error> {
	// `leaf_indices` is supplied by the relayer in the unsigned consensus message;
	// an empty vector previously panicked the runtime via the unchecked `[0]` index
	// after the BEEFY signature and authority membership checks had already succeeded.
	// This verifier checks a single MMR leaf, so reject any proof that does not carry
	// exactly one leaf index.
	if mmr.mmr_proof.leaf_indices.len() != 1 {
		Err(Error::InvalidMmrProof)?
	}
	let leaf_index = mmr.mmr_proof.leaf_indices[0];
	let leaf_hash = H::keccak256(&mmr.latest_mmr_leaf.encode());
	let mmr_size = leaf_index_to_mmr_size(leaf_index);

	let mmr_proof = MmrMerkleProof::<[u8; 32], KeccakMerge<H>>::new(
		mmr_size,
		mmr.mmr_proof.items.iter().map(|h| (*h).into()).collect(),
	);
	let leaf_pos = leaf_index_to_pos(leaf_index);
	let leaf = (leaf_pos, leaf_hash.into());
```

**File:** parachain/runtimes/nexus/src/lib.rs (L744-772)
```rust
/// Nexus routes all BEEFY consensus updates through `pallet-beefy-consensus-proofs`, which
/// requires each proof to pass SP1 zkVM verification before it can advance the BEEFY state.
/// Allowing raw updates through `handle_unsigned` would bypass that requirement entirely, so
/// any batch that carries a BEEFY consensus message is rejected here. `fund_message` is also
/// disabled because it will change the child trie root allowing beefy proofs that have no economic
/// value
///
/// A consensus message only names the state it updates, so we ask the host which client owns
/// that state and compare against BEEFY. Reading from the host remains correct even as more
/// states (Polkadot, Paseo) are bound to the same client over time.
pub struct IsmpCallFilter;
impl Contains<RuntimeCall> for IsmpCallFilter {
	fn contains(call: &RuntimeCall) -> bool {
		use ::ismp::{host::IsmpHost, messaging::Message};
		match call {
			RuntimeCall::Ismp(pallet_ismp::Call::fund_message { .. }) => false,
			RuntimeCall::Ismp(pallet_ismp::Call::handle_unsigned { messages }) => {
				let host = Ismp::default();
				!messages.iter().any(|message| match message {
					Message::Consensus(consensus) =>
						host.consensus_client_id(consensus.consensus_state_id) ==
							Some(ismp_beefy::BEEFY_CONSENSUS_ID),
					_ => false,
				})
			},
			_ => true,
		}
	}
}
```
