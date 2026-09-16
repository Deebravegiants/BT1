Confirmed analog: `HeaderImpl.stateCommitment` in `evm/src/consensus/Types.sol` initializes `mmrRoot`/`childTrieRoot` to their zero default and only overwrites them if an `ISMP_CONSENSUS_ID` digest is found, but the function only guards against a missing `ISMP_TIMESTAMP_ID` digest via `TimestampNotFound`. This mirrors the WavPack `ParseCaffHeaderConfig` bug class: a config/header struct with fields left at their default ("uninitialized" in effect) whenever the malicious input omits the relevant section, with no corresponding validation for that specific field before it's consumed downstream.

### Title
Missing validation of ISMP consensus digest in `HeaderImpl.stateCommitment` allows zero-initialized state/overlay roots to be accepted - (File: evm/src/consensus/Types.sol)

### Summary
`stateCommitment()` derives `overlayRoot` (MMR root) and `stateRoot` (child trie root) purely from an optional `ISMP` consensus digest found in a Substrate header's digest list. If that digest is absent or malformed such that the `ISMP_CONSENSUS_ID` match never triggers, `mmrRoot` and `childTrieRoot` silently stay at their Solidity default of `bytes32(0)` and are returned as a valid `StateCommitment` as long as a distinct `ISMP_TIMESTAMP_ID` digest is present.

### Finding Description [1](#0-0) 

The loop only sets `mmrRoot`/`childTrieRoot` inside the `isConsensus && consensusId == ISMP_CONSENSUS_ID` branch [2](#0-1) . The sanity check at the end of the function only reverts with `TimestampNotFound` when `timestamp == 0`, but performs no equivalent check that `mmrRoot` or `childTrieRoot` were actually populated [3](#0-2) . Since a header can independently carry the `ISMP_TIMESTAMP_ID` digest (setting `timestamp`) without carrying a valid `ISMP_CONSENSUS_ID` digest, the function returns a `StateCommitment{timestamp, overlayRoot: 0x0, stateRoot: 0x0}` instead of rejecting the header.

This function is called from `SP1Beefy.sol`'s `verify()` for every parachain header supplied in a proof, to build the `IntermediateState` array that becomes the trusted state commitments used for downstream state/membership proof verification [4](#0-3) . `EcdsaBeefy.sol` also calls `.stateCommitment()` in the same pattern. The parallel Rust implementation (`fetch_overlay_root_and_timestamp` in `modules/ismp/state-machines/substrate/src/lib.rs`) correctly treats absence differently — it defaults to zero but callers there generally don't allow zero commitments to be used as a real state root the same way — but the Solidity path has no equivalent guard.

### Impact Explanation
If a state commitment with `overlayRoot = 0` and `stateRoot = 0` is accepted into `IntermediateState` and consumed by state-machine clients that later perform membership/non-membership proofs (checking storage or child-trie proofs against `stateRoot`), a zero root either (a) causes all subsequent membership proofs against that height to fail (denial of service / inability to deliver messages for that height), or (b) in merkle libraries where an empty/zero root has trivial-non-membership semantics, could enable a forged non-membership proof to be accepted, allowing an attacker to claim a request/response was never delivered or bypass a required state check. Either outcome maps to "unsound state commitment" / "route unable to deliver messages" categories.

### Likelihood Explanation
Exploitability depends on whether a relayer/prover can submit a parachain header (already SCALE-decoded and matched against the MMR/authority proof in `SP1Beefy`/`EcdsaBeefy`) that carries a timestamp digest but omits or corrupts the ISMP consensus digest, while the surrounding BEEFY/MMR-leaf/authority-signature checks still succeed for the *header hash* (the digests are part of the header that's hashed and verified — so the digests can't be tampered independently of hash matching in the fully-verified case). This significantly limits practical exploitability to chains/situations where headers legitimately omit the ISMP digest (e.g., non-ISMP-enabled parachains) yet are still fed through paths expecting `stateCommitment()`, which reduces confidence this is reachable with attacker-controlled digest content on Hyperbridge's actual tracked parachains. I could not fully verify from available context whether any legitimate/malicious caller can supply a real, hash-matching header for a tracked chain that has a timestamp digest but no consensus digest.

### Recommendation
Add an explicit zero-check (or "digest not found" boolean) for `mmrRoot`/`childTrieRoot` in `HeaderImpl.stateCommitment`, reverting with a dedicated error (e.g., `IsmpConsensusDigestNotFound`) analogous to `TimestampNotFound`, mirroring the Rust `ConsensusDigest`-required checks used elsewhere in the codebase.

### Proof of Concept
Construct (or use) a Substrate header whose digest logs include a valid `ISMP_TIMESTAMP_ID` entry (`ISTM`) but no `ISMP_CONSENSUS_ID` entry (`ISMP`). Feed this header through `Codec.DecodeHeader` and `HeaderImpl.stateCommitment` (as done in `SP1Beefy.verify` at [4](#0-3) ); observe that the call succeeds and returns `overlayRoot == bytes32(0)` and `stateRoot == bytes32(0)` rather than reverting, which downstream state-machine clients would otherwise treat as an invalid/missing commitment.

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

**File:** evm/src/consensus/SP1Beefy.sol (L161-167)
```text
            Header memory header = Codec.DecodeHeader(para.header);
            if (header.number == 0) revert IllegalGenesisBlock();

            StateCommitment memory stateCommitment = header.stateCommitment();
            IntermediateState memory intermediate =
                IntermediateState({stateMachineId: para.id, height: header.number, commitment: stateCommitment});
            intermediates[i] = intermediate;
```
