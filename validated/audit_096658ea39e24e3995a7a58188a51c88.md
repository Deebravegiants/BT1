### Title
`HeaderImpl.stateCommitment()` silently produces a zero `overlayRoot`/`stateRoot` state commitment when the ISMP consensus digest is absent from a header, and `HandlerV2.handleConsensus` stores it without validation - (File: evm/src/consensus/Types.sol)

### Summary
`HeaderImpl.stateCommitment()` extracts `overlayRoot` (MMR root) and `stateRoot` (child-trie root) exclusively from the `ISMP` consensus digest item embedded in a Substrate/parachain header. If that digest item is missing from a header included in a consensus proof, `mmrRoot` and `childTrieRoot` remain at their Solidity default of `bytes32(0)` — the function only reverts (`TimestampNotFound`) if the *timestamp* digest (`ISTM`) is missing, never if the *ISMP consensus* digest is missing. This zero-valued `StateCommitment` is returned as an `IntermediateState` from `EcdsaBeefy.verify`/`SP1Beefy.verify` and is stored unconditionally by `HandlerV2.handleConsensus` → `IHost.storeStateMachineCommitment`, with no check that `overlayRoot`/`stateRoot` are non-zero before persisting, analogous to `TrufMigrator.setMerkleRoot` accepting a zero `merkleRoot`.

### Finding Description
`HeaderImpl.stateCommitment()`: [1](#0-0) 

only assigns `mmrRoot`/`childTrieRoot` inside the loop when it finds a digest with `consensusId == ISMP_CONSENSUS_ID`; if no such digest exists in the header, both variables keep their zero-initialized default. The only sanity check performed is on `timestamp`, not on the roots:
```solidity
if (timestamp == 0) revert TimestampNotFound();
return StateCommitment({timestamp: timestamp, overlayRoot: mmrRoot, stateRoot: childTrieRoot});
```
This function is invoked on every header decoded from an untrusted, relayer-supplied consensus proof in both consensus clients: [2](#0-1) [3](#0-2) 

The resulting `IntermediateState[]` is consumed by `HandlerV2.handleConsensus`, which is a permissionless entry point (callable by any relayer) and stores each commitment with no non-zero check on `overlayRoot`/`stateRoot`: [4](#0-3) 

`EvmHost.storeStateMachineCommitment` likewise performs no validation before writing to storage: [5](#0-4) 

By contrast, the on-chain Substrate consensus-client implementations for GRANDPA/BEEFY (Rust side) explicitly filter which parachains are tracked and where the timestamp comes from, and note that some parachains (e.g. Asset Hub) "never deposit the timestamp digest": [6](#0-5) 

This shows the assumption that timestamp and ISMP-digest presence are coupled is not strictly enforced at the type level for the EVM Solidity path — `HeaderImpl.stateCommitment()` has no equivalent guard tying digest presence to the ISMP consensus digest specifically, and if a header carries a timestamp digest but happens to omit (or a proof fragment splits) the ISMP consensus digest, the function proceeds and produces a poisoned all-zero commitment.

### Impact Explanation
If a zero `StateCommitment` (`overlayRoot == bytes32(0)`, `stateRoot == bytes32(0)`) is stored for a state-machine height, `HandlerV2.handlePostRequests`/`handleGetResponses` explicitly reject it downstream: [7](#0-6) 
```solidity
bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
if (root == bytes32(0)) revert StateCommitmentNotFound();
```
Because `_latestStateMachineHeight[stateMachineId]` is advanced to this poisoned height as part of the same store call, and `storeStateMachineCommitment` is only ever called by the handler when `intermediate.height > latestHeight`, all subsequent legitimate proofs for smaller/equal heights are also rejected by the height-monotonicity gate in `handleConsensus` (`if (latestHeight != 0 && intermediate.height > latestHeight)`), so the counterparty route for that state machine becomes unable to deliver POST/GET messages until a new, higher, non-zero-commitment update arrives — a temporary-to-persistent denial of message delivery for that route (route unable to deliver messages).

### Likelihood Explanation
This requires a header, legitimately finalized and signed by the trusted authority set, whose consensus digest logs lack an `ISMP` consensus item while a timestamp digest is present (or a proof-construction bug/malformed-but-validly-signed header stream that a permissionless relayer can submit as-is, since `handleConsensus` is open to any caller and does no additional validation of intermediate commitments). This is plausible under real deployment conditions where a tracked state machine only intermittently deposits the ISMP digest, or during a runtime-upgrade / migration window where digest emission changes; it does not require a malicious admin, only a relayer submitting a consensus proof containing such a header.

### Recommendation
In `HeaderImpl.stateCommitment()`, track whether the `ISMP_CONSENSUS_ID` digest was actually found and revert if not (mirroring the existing timestamp check), e.g.:
```solidity
bool foundIsmpDigest;
...
if (self.digests[j].isConsensus && self.digests[j].consensus.consensusId == ISMP_CONSENSUS_ID) {
    mmrRoot = ...; childTrieRoot = ...; foundIsmpDigest = true;
}
...
if (!foundIsmpDigest) revert IsmpDigestNotFound();
```
Additionally, add a defense-in-depth check in `HandlerV2.handleConsensus` (or in `EvmHost.storeStateMachineCommitment`) to reject/skip intermediates whose `overlayRoot`/`stateRoot` are `bytes32(0)`, so a zero commitment can never be persisted regardless of which upstream verifier produced it.

### Proof of Concept
1. A relayer submits a BEEFY (or SP1) consensus proof to `HandlerV2.handleConsensus` containing a `ParachainHeader` whose SCALE-encoded digest list includes an `ISTM` (timestamp) consensus item but omits the `ISMP` consensus item (either because the tracked chain's block genuinely lacks it, or because the relayer crafts/selects such a header while all cryptographic/MMR/authority checks still pass for the *header hash*, since those only need the header hash to match, not its digest contents being fully well-formed w.r.t. ISMP semantics).
2. `Codec.DecodeHeader` parses the digests; `HeaderImpl.stateCommitment()` is called in `verifyParachainHeaderProof` (EcdsaBeefy) or `verifyConsensus` (SP1Beefy): `timestamp != 0` so no revert, but `mmrRoot == bytes32(0)` and `childTrieRoot == bytes32(0)`.
3. `verify()` returns an `IntermediateState` with `commitment.overlayRoot == 0`, `commitment.stateRoot == 0`, for a height greater than the currently stored `latestStateMachineHeight` for that state machine.
4. `HandlerV2.handleConsensus` stores this via `host.storeStateMachineCommitment`, updating `_latestStateMachineHeight[stateMachineId]` to this new height with a zero commitment.
5. Any subsequent `handlePostRequests`/`handleGetResponses` call against that height reverts with `StateCommitmentNotFound()`, and no future consensus update below/at that height can override it due to the `intermediate.height > latestHeight` monotonicity check — freezing message delivery on that route until a strictly higher legitimate update supersedes it.

### Citations

**File:** evm/src/consensus/Types.sol (L211-231)
```text
    function stateCommitment(Header memory self) internal pure returns (StateCommitment memory) {
        bytes32 mmrRoot;
        bytes32 childTrieRoot;
        uint256 timestamp;

        for (uint256 j = 0; j < self.digests.length; j++) {
            if (self.digests[j].isConsensus && self.digests[j].consensus.consensusId == ISMP_CONSENSUS_ID) {
                mmrRoot = Bytes.toBytes32(Bytes.substr(self.digests[j].consensus.data, 0, 32));
                childTrieRoot = Bytes.toBytes32(Bytes.substr(self.digests[j].consensus.data, 32));
            }

            if (self.digests[j].isConsensus && self.digests[j].consensus.consensusId == ISMP_TIMESTAMP_ID) {
                timestamp = ScaleCodec.decodeUint256(self.digests[j].consensus.data);
            }
        }

        // sanity check
        if (timestamp == 0) revert TimestampNotFound();

        return StateCommitment({timestamp: timestamp, overlayRoot: mmrRoot, stateRoot: childTrieRoot});
    }
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L208-221)
```text
        for (uint256 i = 0; i < len; i++) {
            Parachain memory para = proof.parachains[i];
            Header memory header = Codec.DecodeHeader(para.header);
            if (header.number == 0) revert IllegalGenesisBlock();

            leaves[i] = MerkleMultiProof.Leaf(
                para.index,
                keccak256(bytes.concat(ScaleCodec.encode32(uint32(para.id)), ScaleCodec.encodeBytes(para.header)))
            );

            StateCommitment memory commitment = header.stateCommitment();
            intermediates[i] =
                IntermediateState({stateMachineId: para.id, height: header.number, commitment: commitment});
        }
```

**File:** evm/src/consensus/SP1Beefy.sol (L160-167)
```text
            ParachainHeader memory para = proof.headers[i];
            Header memory header = Codec.DecodeHeader(para.header);
            if (header.number == 0) revert IllegalGenesisBlock();

            StateCommitment memory stateCommitment = header.stateCommitment();
            IntermediateState memory intermediate =
                IntermediateState({stateMachineId: para.id, height: header.number, commitment: stateCommitment});
            intermediates[i] = intermediate;
```

**File:** evm/src/core/HandlerV2.sol (L155-163)
```text
        uint256 intermediatesLen = intermediates.length;
        for (uint256 i = 0; i < intermediatesLen; i++) {
            IntermediateState memory intermediate = intermediates[i];
            uint256 latestHeight = host.latestStateMachineHeight(intermediate.stateMachineId);
            if (latestHeight != 0 && intermediate.height > latestHeight) {
                StateMachineHeight memory stateMachineHeight =
                    StateMachineHeight({stateMachineId: intermediate.stateMachineId, height: intermediate.height});
                host.storeStateMachineCommitment(stateMachineHeight, intermediate.commitment);
            }
```

**File:** evm/src/core/HandlerV2.sol (L199-202)
```text
        bytes32 root = host.stateMachineCommitment(request.proof.height).overlayRoot;
        if (root == bytes32(0)) revert StateCommitmentNotFound();
        bool valid = MerkleMountainRange.VerifyProof(root, request.proof.multiproof, leaves, request.proof.leafCount);
        if (!valid) revert InvalidProof();
```

**File:** evm/src/core/EvmHost.sol (L687-699)
```text
    function storeStateMachineCommitment(StateMachineHeight memory height, StateCommitment memory commitment)
        external
        restrict(_hostParams.handler)
    {
        _stateCommitments[height.stateMachineId][height.height] = commitment;
        _stateCommitmentsUpdateTime[height.stateMachineId][height.height] = block.timestamp;
        _latestStateMachineHeight[height.stateMachineId] = height.height;

        emit StateMachineUpdated({
            stateMachineId: this.stateMachineId(_hostParams.hyperbridge, height.stateMachineId), 
            height: height.height
        });
    }
```

**File:** modules/ismp/state-machines/substrate/src/lib.rs (L417-427)
```rust
	// chains without pallet-ismp never deposit the timestamp digest, so their block time can
	// only come from the slot they were authored in
	if digest_result.timestamp == 0 {
		digest_result.timestamp = slot
			.map(|slot| Duration::from_millis((*slot).saturating_mul(slot_duration)).as_secs())
			.unwrap_or_default();
	}

	if digest_result.timestamp == 0 {
		Err(Error::Custom("Timestamp not found".into()))?
	}
```
