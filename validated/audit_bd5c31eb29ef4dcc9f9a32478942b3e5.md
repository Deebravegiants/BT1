Found the key issue. In `EcdsaBeefy.sol`, `checkParticipationThreshold(uint256 len, uint256 total)` only enforces a **lower bound** (`len >= (2*total/3)+1`) and never checks an **upper bound** relative to `authoritySet.len`. `sigLen` is taken directly from attacker/relayer-supplied calldata (`relayProof.signedCommitment.votes.length`) with no cap, so a caller can submit an arbitrarily large `votes` array. Every entry drives an `ECDSA.recover` (expensive `ecrecover` precompile call) plus a `MerkleMultiProof.Leaf` array build, all before the merkle-membership proof is checked. This mirrors CVE-2018-0732's pattern: an attacker-controlled size/length parameter (there, a DH prime; here, a signature-vote array) drives unbounded expensive cryptographic work before any validity check on that same input rejects it.### Title
Unbounded attacker-controlled `votes` array in `EcdsaBeefy.verifyMmrUpdateProof` allows gas-exhaustion DoS on BEEFY consensus updates - (File: evm/src/consensus/EcdsaBeefy.sol)

### Summary
`EcdsaBeefy.verify` → `verifyMmrUpdateProof` takes `sigLen = relayProof.signedCommitment.votes.length` directly from calldata submitted by any unprivileged relayer and only checks a **lower bound** on it via `checkParticipationThreshold`. There is no upper bound tying `sigLen` to the trusted `authoritySet.len`. Every entry in `votes` triggers an expensive `ECDSA.recover` (secp256k1 `ecrecover`) call and array write before the cheap merkle membership check (`MerkleMultiProof.VerifyProof`) that would ultimately reject bogus/padding entries. This is directly analogous to CVE-2018-0732: an attacker-controlled size parameter (there, a DH prime; here, an array length) drives unbounded expensive cryptographic computation before the input is validated against the parameter it should be bounded by.

### Finding Description [1](#0-0) 

```solidity
uint256 sigLen = relayProof.signedCommitment.votes.length;
...
if (!checkParticipationThreshold(sigLen, authoritySet.len)) revert SuperMajorityRequired();
...
MerkleMultiProof.Leaf[] memory authorities = new MerkleMultiProof.Leaf[](sigLen);
for (uint256 i = 0; i < sigLen; i++) {
    Vote memory vote = relayProof.signedCommitment.votes[i];
    address authority = ECDSA.recover(commitmentHash, vote.signature);
    authorities[i] =
        MerkleMultiProof.Leaf({index: vote.authorityIndex, hash: keccak256(abi.encodePacked(authority))});
}
bool valid = MerkleMultiProof.VerifyProof(authoritySet.root, relayProof.proof, authorities, authoritySet.len);
```

`checkParticipationThreshold` is defined as: [2](#0-1) 

```solidity
function checkParticipationThreshold(uint256 len, uint256 total) internal pure returns (bool) {
    return len >= ((2 * total) / 3) + 1;
}
```

This function enforces only `len >= (2*total/3)+1` — a floor — and imposes **no ceiling** relating `sigLen` to `authoritySet.len`. `Vote[] votes` is an ABI-decoded, caller-supplied array with no `MaxVotes`/length cap anywhere in `Types.sol` or `EcdsaBeefy.sol` (confirmed via search of the type definitions and grep for `MAX_VOTES`/`votes.length`, none exist). Since `votes.length` can vastly exceed `authoritySet.len` (e.g. thousands of dummy/garbage-signature entries appended to a small honest quorum), the contract performs an `ECDSA.recover` call — a relatively gas-expensive `ecrecover`-based operation plus memory writes — for every one of those entries **before** the cheap `MerkleMultiProof.VerifyProof` check that would reject spurious authority indices. This ordering means the attacker pays for calldata but forces the verifying transaction (submitted by any relayer/anyone routing through `ConsensusRouter.verify`) to burn a multiple of the "true cost" of verification, and can push the call past the block gas limit, causing legitimate consensus proofs to revert (out-of-gas) purely due to gas-cost amplification from oversized `votes`.

Compare this to the Rust-side beefy verifier (`modules/consensus/beefy/verifier/src/lib.rs`), which has the identical structural weakness — `signatures_length` is likewise unbounded and processed through `secp256k1_recover` for every signature before the merkle check — but there the cost model is pallet weight rather than a hard EVM gas ceiling, so the amplification is comparatively bounded by the extrinsic's weight metering. The EVM path (`EcdsaBeefy.sol`), reachable by any relayer calling the public `ConsensusRouter.verify`/`IConsensusV2.verify` entry point with no admin gating, has no such analogous protective cap, and is the strongest reachable instance of the analog.

### Impact Explanation
This is a route-availability / denial-of-service issue on the consensus-update path that all IBC/ISMP message delivery and state-proof verification for EVM deployments with the ECDSA BEEFY consensus client ultimately depend on (`EcdsaBeefy` is one of the two verifiers wired through `ConsensusRouter`). An attacker who can submit (or induce a relayer to submit) a `RelayChainProof` with an inflated `votes` array can force the consensus-update transaction to revert from gas exhaustion, or make honest relayers pay dramatically inflated gas costs to get a legitimate BEEFY update accepted — effectively a route unable to deliver messages until callers learn to strip the array server-side (which the on-chain verifier itself does not enforce). It does not directly cause fund theft, but it satisfies the "route unable to deliver messages" acceptance criterion for a consensus-verification DoS.

### Likelihood Explanation
High feasibility: `ConsensusRouter.verify`/`EcdsaBeefy.verify` are `external`/permissionless entry points that decode caller-supplied `bytes calldata proof` with `abi.decode`; nothing restricts who calls them or what `votes.length` may be. Constructing an oversized `votes` array with syntactically valid `Vote{signature, authorityIndex}` entries (garbage 65-byte signatures still parse through `ECDSA.recover`, they simply produce a wrong/no `authority` value) costs only calldata gas to the attacker while amplifying `ecrecover` calls on the verifier side.

### Recommendation
Add an explicit upper bound in `verifyMmrUpdateProof`/`checkParticipationThreshold` (or immediately after computing `sigLen`) rejecting `sigLen > authoritySet.len`, mirroring the fix already applied elsewhere in this codebase for analogous "attacker-controlled array length drives expensive per-item pre-validation work" issues (e.g. the `MAX_PROOF_DEPTH` bound added in `modules/consensus/pharos/primitives/src/spv.rs` and the duplicate-key rejection added ahead of trie work in `modules/ismp/state-machines/evm/src/lib.rs`). Apply the same cap to the Rust `verify_mmr_update_proof` in `modules/consensus/beefy/verifier/src/lib.rs` for consistency across both verifier implementations.

### Proof of Concept
1. Take any historically valid `RelayChainProof` whose `signedCommitment.votes` contains exactly the honest supermajority (e.g. `k = (2*total/3)+1` real votes).
2. Append `N` additional `Vote` entries with arbitrary 65-byte signature bytes and arbitrary `authorityIndex` values (these need not be valid — they only need to parse as `bytes`/`uint256`).
3. Call `ConsensusRouter.verify(previousState, encodedProof)` (or `EcdsaBeefy.verify` directly) with this proof.
4. `checkParticipationThreshold(k + N, total)` still passes because it only checks the lower bound.
5. The loop at lines 154-159 executes `ECDSA.recover` `k + N` times before `MerkleMultiProof.VerifyProof` is reached; increasing `N` linearly increases gas consumption with no cap, until the call reverts out-of-gas or costs an arbitrarily large multiple of the honest-case gas cost.

### Citations

**File:** evm/src/consensus/EcdsaBeefy.sol (L127-162)
```text
        uint256 sigLen = relayProof.signedCommitment.votes.length;
        uint256 latestHeight = relayProof.signedCommitment.commitment.blockNumber;
        Commitment memory commitment = relayProof.signedCommitment.commitment;
        if (
            commitment.validatorSetId != trustedState.currentAuthoritySet.id
                && commitment.validatorSetId != trustedState.nextAuthoritySet.id
        ) {
            revert UnknownAuthoritySet();
        }

        bool isCurrentAuthorities = commitment.validatorSetId == trustedState.currentAuthoritySet.id;
        AuthoritySetCommitment memory authoritySet =
            isCurrentAuthorities ? trustedState.currentAuthoritySet : trustedState.nextAuthoritySet;
        if (!checkParticipationThreshold(sigLen, authoritySet.len)) revert SuperMajorityRequired();

        uint256 payloadLength = commitment.payload.length;
        bytes32 mmrRoot;
        for (uint256 i = 0; i < payloadLength; i++) {
            if (commitment.payload[i].id == MMR_ROOT_PAYLOAD_ID && commitment.payload[i].data.length == 32) {
                mmrRoot = Bytes.toBytes32(commitment.payload[i].data);
            }
        }
        if (mmrRoot == bytes32(0)) revert MmrRootHashMissing();

        // verify the commitment
        bytes32 commitmentHash = keccak256(Codec.Encode(commitment));
        MerkleMultiProof.Leaf[] memory authorities = new MerkleMultiProof.Leaf[](sigLen);
        for (uint256 i = 0; i < sigLen; i++) {
            Vote memory vote = relayProof.signedCommitment.votes[i];
            address authority = ECDSA.recover(commitmentHash, vote.signature);
            authorities[i] =
                MerkleMultiProof.Leaf({index: vote.authorityIndex, hash: keccak256(abi.encodePacked(authority))});
        }

        bool valid = MerkleMultiProof.VerifyProof(authoritySet.root, relayProof.proof, authorities, authoritySet.len);
        if (!valid) revert InvalidAuthoritiesProof();
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L240-243)
```text
    // @dev Check for supermajority participation.
    function checkParticipationThreshold(uint256 len, uint256 total) internal pure returns (bool) {
        return len >= ((2 * total) / 3) + 1;
    }
```
