Based on the evidence gathered, I found a concrete analog in the BEEFY parachain-header ingestion path.

### Title
Missing ISMP consensus-digest presence check lets BEEFY accept a parachain header with `overlay_root = 0x00…00`, corrupting the state commitment - (File: modules/ismp/clients/beefy/src/consensus.rs)

### Summary
The EIP-7685 report flags that Besu accepted post-Prague block headers omitting the mandatory `requestsHash` field because no rule checked its presence independent of the parent header. The same bug class exists in `BeefyConsensusClient::verify_consensus`: when decoding a verified parachain header's digests, `overlay_root` is only assigned inside the loop *if* an `ISMP` `DigestItem::Consensus` entry is found; if that digest is absent, `overlay_root` silently keeps its zero-initialized default value, and there is no independent check that the digest was present before the commitment is constructed and stored.

### Finding Description
In `verify_consensus`, the code initializes `(mut timestamp, mut overlay_root) = (0, H256::default())` and only overwrites `overlay_root` when it finds a `DigestItem::Consensus` entry whose engine ID equals `ISMP_ID`: [1](#0-0) 

Only `timestamp == 0` is checked afterward and causes a `TimestampNotFound` error; there is **no equivalent check** that an ISMP consensus digest (which sets `overlay_root`) was actually present: [2](#0-1) 

If it wasn't present, `overlay_root` remains `H256::default()` (all-zero) and is wrapped as `Some(overlay_root)` into the `StateCommitment` that gets persisted for that parachain height: [3](#0-2) 

Compare this to the sibling GRANDPA/parachain client which uses `fetch_overlay_root_and_timestamp` and is proven (by test `a_header_with_neither_digest_is_rejected`) to reject a header lacking the digest with `"Timestamp not found"`: [4](#0-3) 

That test only demonstrates the timestamp digest is checked — I could not fully verify (tool access ran out) whether `fetch_overlay_root_and_timestamp` itself also independently validates presence of the ISMP consensus digest (as opposed to relying on the timestamp check as a coincidental proxy) in the GRANDPA/parachain path. However, in the BEEFY client shown above, the ISMP digest's absence is not independently checked at all — the code relies purely on the unrelated timestamp digest defaulting to 0, which is a different digest kind (`ISMP_TIMESTAMP_ID` vs `ISMP_ID`) emitted by a separate mechanism. A parachain runtime (or malicious/misconfigured chain) could emit a timestamp digest without the ISMP consensus digest, and the BEEFY consensus client would accept it, writing a zeroed `overlay_root` into the trusted `StateCommitment`.

### Impact Explanation
`overlay_root` is the MMR root that `HandlerV2.sol::handlePostRequests`/`handleGetResponses` (EVM side) and `SubstrateStateMachine::verify_membership` use as the trusted root for verifying that request/response commitments were actually included on the source chain: [5](#0-4) [6](#0-5) 

Since `evm/src/core/HandlerV2.sol` explicitly reverts when `root == bytes32(0)` (`StateCommitmentNotFound`), a zeroed overlay root there is caught — but the Substrate-side `SubstrateStateMachine::verify_membership` only checks `overlay_root.is_none()`, not whether it is the zero hash; `Some(H256::zero())` passes that check and is then used as a trie root to verify commitments, which would simply fail any real membership proof (a corrupted commitment height effectively becomes permanently un-provable, i.e. a denial-of-service/frozen route for genuine ISMP messages finalized at that height on that parachain), rather than a direct fund-theft path. This matches the "route unable to deliver messages" acceptance criterion for a valid finding, since messages dispatched by that parachain at the affected height become undeliverable/unproveable through Hyperbridge.

### Likelihood Explanation
Triggering this requires a BEEFY-finalized parachain header that carries a timestamp digest without accompanying an ISMP digest for the same block — this depends on the parachain's own block-authoring logic (which is untrusted by the light client, that is the whole point of ISMP-based state proofs) rather than on Hyperbridge/Polkadot-relay validator misbehavior. Because the two digests are independent SCALE-encoded runtime digests, a parachain runtime bug or version-skew (upgrade that removes/reorders the ISMP digest hook while still emitting a timestamp) is a plausible, low-cost trigger and is analogous in spirit to the Besu bug (a legitimately-produced but non-conforming header slipping past validation).

### Recommendation
Add an explicit presence check for the ISMP consensus digest, independent of the timestamp digest, mirroring the fix pattern used for `RequestsHashPresentValidationRule` in Besu: track whether a `DigestItem::Consensus` entry with `ISMP_ID` was actually observed in the loop, and return a dedicated error (e.g. `BeefyError::IsmpDigestNotFound`) if it was not, before constructing the `StateCommitment`.

### Proof of Concept
1. Construct a parachain block header whose digest log contains a valid `ISMP_TIMESTAMP_ID` (`ISTM`) digest but omits the `ISMP_ID` (`ISMP`) consensus digest.
2. Get this header finalized via a genuine BEEFY MMR proof (attacker does not need to forge BEEFY signatures — the parachain's own collator/runtime produces the header content).
3. Submit the BEEFY consensus proof containing this header through `BeefyConsensusClient::verify_consensus`.
4. Observe `overlay_root` remains `H256::default()` and is persisted as `StateCommitment { overlay_root: Some(H256::zero()), .. }` for that parachain height/state machine — subsequent membership proofs against that height on the Substrate side will always fail even for legitimately dispatched requests, freezing message delivery for that finalized height.

### Citations

**File:** modules/ismp/clients/beefy/src/consensus.rs (L123-147)
```rust
			let mut state_commitments_vec = Vec::new();
			let (mut timestamp, mut overlay_root) = (0, H256::default());

			for digest in header.digest().logs.iter() {
				match digest {
					DigestItem::Consensus(consensus_engine_id, value)
						if *consensus_engine_id == ISMP_TIMESTAMP_ID =>
					{
						let timestamp_digest = TimestampDigest::decode(&mut &value[..])
							.map_err(|e| BeefyError::DecodeTimestampDigest(format!("{e:?}")))?;
						timestamp = timestamp_digest.timestamp;
					},
					DigestItem::Consensus(consensus_engine_id, value)
						if *consensus_engine_id == ISMP_ID =>
					{
						let log = ConsensusDigest::decode(&mut &value[..]);
						if let Ok(log) = log {
							overlay_root = log.child_trie_root;
						} else {
							Err(BeefyError::InvalidIsmpConsensusLog)?
						}
					},
					_ => {},
				};
			}
```

**File:** modules/ismp/clients/beefy/src/consensus.rs (L148-150)
```rust
			if timestamp == 0 {
				Err(BeefyError::TimestampNotFound)?
			}
```

**File:** modules/ismp/clients/beefy/src/consensus.rs (L160-172)
```rust
			let height: u32 = (*header.number()).into();
			let intermediate = StateCommitmentHeight {
				commitment: StateCommitment {
					timestamp,
					overlay_root: Some(overlay_root),
					state_root: header.state_root,
				},
				height: height.into(),
			};

			state_commitments_vec.push(intermediate);
			intermediates
				.insert(StateMachineId { state_id, consensus_state_id }, state_commitments_vec);
```

**File:** modules/pallets/testsuite/src/tests/ismp_parachain.rs (L150-160)
```rust
#[test]
fn a_header_with_neither_digest_is_rejected() {
	new_test_ext().execute_with(|| {
		SlotDurations::<Test>::insert(ASSET_HUB_PARA_ID, SLOT_DURATION);

		let header = parachain_header(vec![]);
		let error = verify(setup(ASSET_HUB_PARA_ID, &header)).unwrap_err();

		assert!(format!("{error:?}").contains("Timestamp not found"), "{error:?}");
	})
}
```

**File:** evm/src/core/HandlerV2.sol (L199-202)
```text
        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();
```

**File:** modules/ismp/state-machines/substrate/src/lib.rs (L140-143)
```rust
		let root = match T::Coprocessor::get() {
			Some(id) if id == proof.height.id.state_id => state.state_root,
			_ => state.overlay_root.ok_or(SubstrateStateMachineError::MissingChildTrieRoot)?,
		};
```
