### Title
Unvalidated ISMP digest length before fixed-offset `Bytes.substr` reads panics `EcdsaBeefy`/`SP1Beefy` consensus verification on a crafted parachain header - (File: evm/src/consensus/Types.sol)

### Summary
`HeaderImpl.stateCommitment()` reads `mmrRoot`/`childTrieRoot` out of the ISMP consensus digest's raw `data` bytes at fixed offsets `[0:32]` and `[32:64]` without first checking that `data.length >= 64`. This is the same bug class as CVE-2021-44501 (GT.M's `ZRead` NULL-pointer dereference on crafted input): a fixed-size read is performed on attacker-influenced, variable-length input without a length precondition check.

### Finding Description
`Codec.DecodeHeader` (`evm/src/consensus/Codec.sol:70-102`) parses a SCALE-encoded Substrate header supplied inside a `ParachainHeader`/`Parachain` proof element and populates each `Digest.consensus.data` directly from attacker-controlled bytes via `decodeDigestItem` (`Codec.sol:104-110`), which reads an arbitrary attacker-declared length with no minimum-size constraint.

That decoded header is then passed to `header.stateCommitment()`: [1](#0-0) 

```
mmrRoot = Bytes.toBytes32(Bytes.substr(self.digests[j].consensus.data, 0, 32));
childTrieRoot = Bytes.toBytes32(Bytes.substr(self.digests[j].consensus.data, 32));
```

Neither call is preceded by a check that `self.digests[j].consensus.data.length >= 64`. If a submitted parachain header carries a digest with `consensusId == ISMP_CONSENSUS_ID` ("ISMP") but a `data` payload shorter than 64 bytes (or empty), `Bytes.substr`/`Bytes.toBytes32` from the external `solidity-merkle-trees` library is invoked with an out-of-range slice. This function is reachable from the permissionless entry point:

- `EvmHost`/`HandlerV2.handleConsensus` → `IConsensusV2(consensusClient).verify()` → `EcdsaBeefy.verify` → `verifyParachainHeaderProof` (`evm/src/consensus/EcdsaBeefy.sol:198-229`) → `Codec.DecodeHeader` + `header.stateCommitment()`.
- Same path in `SP1Beefy.sol:151-168`.

Both `EcdsaBeefy.verify` and `SP1Beefy`'s verification are called by anyone submitting a consensus proof via `HandlerV2.handleConsensus`, which is explicitly permissionless (`evm/src/core/HandlerV2.sol:144-150`).

Because the `Bytes` library source is external (`@polytope-labs/solidity-merkle-trees`, not indexed in this repo), the exact runtime behavior of `Bytes.substr`/`Bytes.toBytes32` on out-of-range input could not be directly confirmed from this codebase — but regardless of whether it reverts (denial-of-service on legitimate consensus/message delivery) or performs an unchecked low-level memory copy that reads adjacent memory (returning attacker-uncontrolled but incorrect `mmrRoot`/`childTrieRoot` values into a persisted `StateCommitment`), both outcomes match the report's required impact classes: either "a route unable to deliver messages" (permanent revert on a maliciously short-but-otherwise-valid digest) or "unsound state commitment" (corrupted `overlayRoot`/`stateRoot` silently accepted into consensus state).

This directly parallels the CVE's root cause: a crafted/short input reaching a fixed-length read routine without a prior length check, causing the operation to crash or behave unsafely.

### Impact Explanation
`stateCommitment()` produces the `StateCommitment` (`overlayRoot`, `stateRoot`, `timestamp`) that is stored as an `IntermediateState` and later trusted by `HandlerV2.handlePostRequests`/`handleGetResponses` for message and state-proof verification. If the digest-length precondition is violated:
- The consensus update transaction reverts unpredictably for a specific crafted parachain header, which can be used to grief relayer consensus submissions (any consensus update that includes such a header as one of possibly many `parachains[]` entries fails the entire batch, since `verifyParachainHeaderProof` loops over all `proof.parachains` and a single malformed header aborts the whole call) — a form of "route unable to deliver messages" for as long as attacker keeps resubmitting/mixing malformed headers, though this requires the header to still pass the earlier MMR-leaf/multiproof membership check to be routed into `stateCommitment()`.
- Alternatively, if the underlying library performs an unchecked low-level copy rather than reverting, a garbage/incorrect `mmrRoot`/`childTrieRoot` could be committed as a trusted `StateCommitment`, undermining membership/non-membership proof verification for that parachain height.

### Likelihood Explanation
Reaching this code path requires the header, with its short/adversarial ISMP digest, to actually pass the earlier merkle-multi-proof check binding it into the trusted `headsRoot` (via `MerkleMultiProof.VerifyProof`) — i.e., the header content itself must be a genuine, currently finalized parachain header (or one crafted by a colluding/majority-controlled relay-chain authority set for BEEFY, which is out of scope per the rules excluding malicious-collator/malicious-peer scenarios). Under the current pallet-ismp runtime, legitimate parachains always deposit a 64-byte ISMP consensus digest, so exploiting this in practice would require either a non-standard/misconfigured tracked parachain whose digest is shorter, or a bug/edge case elsewhere that allows a non-conforming digest to be authored. Given this constraint, likelihood is Low-to-Medium and could not be fully confirmed without access to the external `Bytes.sol` implementation.

### Recommendation
In `HeaderImpl.stateCommitment()` (`evm/src/consensus/Types.sol`), before performing the two `Bytes.substr` calls, explicitly check `self.digests[j].consensus.data.length == 64` (or `>= 64`) for the `ISMP_CONSENSUS_ID` case, and skip/treat the digest as absent (or revert with a clear error) otherwise — mirroring the defensive length checks already applied elsewhere in this codebase (e.g., `modules/trees/ethereum/src/node_codec.rs`'s empty-HP-prefix guard and `modules/consensus/pharos/primitives/src/spv.rs`'s `SlotOutOfBounds` checks).

### Proof of Concept
1. Craft a SCALE-encoded Substrate header whose digest list includes one `DigestItem::Consensus` entry with `consensusId = b"ISMP"` and `data` shorter than 64 bytes (e.g., 10 bytes), alongside a valid `ISTM` timestamp digest so the `TimestampNotFound` guard is not triggered.
2. Include this header as a `Parachain` leaf in a `ParachainProof` whose merkle-multi-proof correctly binds it against a genuine `headsRoot` (as would occur for an actually finalized parachain block carrying this crafted digest, or via a compromised relay authority set scenario).
3. Submit via `HandlerV2.handleConsensus(host, proof)` where `proof` decodes to `(RelayChainProof, ParachainProof)` for `EcdsaBeefy.verify`.
4. Observe that `Codec.DecodeHeader` successfully decodes the short digest (no length floor is enforced in `decodeDigestItem`), and `header.stateCommitment()` then calls `Bytes.substr(data, 0, 32)`/`Bytes.substr(data, 32)` on the 10-byte `data`, triggering either a revert deep inside the external library or an out-of-bounds memory read — neither of which is caught or defended against in `Types.sol`.

### Citations

**File:** evm/src/consensus/Types.sol (L211-225)
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
```
