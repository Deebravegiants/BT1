### Title
Unauthenticated `collator_peer_id` in parachain inherent allows forging UMP `ApprovedPeer` reputation signal for arbitrary peers - (File: cumulus/pallets/parachain-system/src/lib.rs)

### Summary
`set_validation_data` copies the collator-supplied `collator_peer_id` field of `ParachainInherentData` directly into `PendingApprovedPeer::<T>` with no cryptographic binding to the block author's actual libp2p identity. Since the inherent is attacker-authored data (any account/collator producing blocks for the parachain controls it), an attacker can set `collator_peer_id` to any `ApprovedPeerId` bytes it chooses, causing the runtime to later emit a UMP `ApprovedPeer` signal for a peer that never did any work.

### Finding Description
`ParachainInherentData::collator_peer_id: Option<ApprovedPeerId>` is a plain, unauthenticated field supplied by whoever builds the block [1](#0-0) . In `set_validation_data`, this value is consumed with no validation against the actual collator/authoring identity:

```rust
match collator_peer_id {
    Some(peer_id) => PendingApprovedPeer::<T>::put(peer_id),
    None => PendingApprovedPeer::<T>::kill(),
}
``` [2](#0-1) 

The `ApprovedPeerId` type is only constrained by a max-length check (`try_from`, up to 64 bytes) with no signature, key, or origin binding tying the byte string to the peer that actually authored/gossiped the candidate. The inherent is a mandatory, unsigned inherent executed exactly once per block via `on_initialize`-adjacent logic in this same extrinsic — it is not gated by any origin check comparable to `ensure_signed`/`ensure_root`; the only "authorization" is the ability to author a parachain block (i.e., be an active collator), which the threat model explicitly treats as attacker-controlled ("attacker only needs collator/authoring capability").

Because `PendingApprovedPeer` is later drained to build a UMP `ApprovedPeer` signal sent to the relay chain (confirmed by the storage's purpose and the field's doc comment: "later sent by the parachain to the relay chain via a UMP signal to promote the reputation of the given peer ID"), any bytes the collator places there for an unrelated/observed `PeerId` will be propagated upstream as if that peer contributed to producing the block. There is no verification step in `set_validation_data` (or elsewhere before signal emission) that the claimed `peer_id` corresponds to the network identity that actually gossiped/authored the corresponding candidate.

### Impact Explanation
This allows forging reputation-relevant UMP `ApprovedPeer` signals for arbitrary `PeerId`s the attacker does not control, simply by observing peer IDs on the network and inserting them into the inherent it authors. This is a network-trust/accounting bypass: reputation credit intended for peers that genuinely assisted collation/backing can be misattributed to unrelated nodes, undermining the integrity of whatever downstream peer-reputation/approval mechanism consumes the `ApprovedPeer` signal on the relay chain side.

### Likelihood Explanation
The only precondition is the ability to author blocks for the parachain (an already-permitted collator role), and the client-side code that normally derives the real peer ID for this field is not enforced by the runtime — the runtime trusts whatever inherent data it receives. Since the inherent field is a `ProvideInherentData`-supplied value, not a signed/verified statement, a malicious or compromised collator client can populate it arbitrarily on every block it authors, making the forgery trivially repeatable without any additional privilege escalation.

### Recommendation
Do not let the runtime trust an arbitrary, unauthenticated `collator_peer_id` value. Either:
- Remove/replace this mechanism with one where the peer ID is bound to a signature or on-chain-verifiable proof of authorship (e.g., signed by the collator's session/collator key and checked against the actual reporting collator for that block), or
- Move the "approved peer" determination fully to a relay-chain/node-level mechanism that observes real network behavior directly (peer connections, statement distribution, etc.) instead of trusting collator-supplied claims embedded in the parachain block, or
- At minimum, add a runtime-side check correlating `collator_peer_id` against an authenticated source (e.g., the collator's registered `CollatorId` mapped to a registered `PeerId`) before calling `PendingApprovedPeer::<T>::put(peer_id)`.

### Proof of Concept
Rust unit test in `cumulus/pallets/parachain-system/src/tests.rs`:
1. Build a `ParachainInherentData` with `collator_peer_id: Some(ApprovedPeerId::try_from(arbitrary_bytes).unwrap())`, where `arbitrary_bytes` represents a `PeerId` not controlled by the test's simulated collator (e.g., a hardcoded, unrelated libp2p peer ID byte string).
2. Call `ParachainSystem::set_validation_data(inherent_origin, inherent_data)` in the mock runtime.
3. Assert `PendingApprovedPeer::<Test>::get() == Some(arbitrary_bytes)` succeeds regardless of any cryptographic relationship between the test's "actual" collator identity and `arbitrary_bytes`.
4. Assert that no error/rejection occurs and that a subsequent drain into the UMP outbound queue (wherever `PendingApprovedPeer` is consumed to build the `ApprovedPeer` signal) would forward this arbitrary value unchanged, demonstrating the missing binding/verification step.

### Citations

**File:** cumulus/primitives/parachain-inherent/src/lib.rs (L110-117)
```rust
	/// Contains the relay parent header and its descendants.
	/// This information is used to ensure that a parachain node builds blocks
	/// at a specified offset from the chain tip rather than directly at the tip.
	pub relay_parent_descendants: Vec<RelayHeader>,
	/// Contains the collator peer ID, which is later sent by the parachain to the
	/// relay chain via a UMP signal to promote the reputation of the given peer ID.
	pub collator_peer_id: Option<ApprovedPeerId>,
}
```

**File:** cumulus/pallets/parachain-system/src/lib.rs (L818-821)
```rust
			match collator_peer_id {
				Some(peer_id) => PendingApprovedPeer::<T>::put(peer_id),
				None => PendingApprovedPeer::<T>::kill(),
			}
```
