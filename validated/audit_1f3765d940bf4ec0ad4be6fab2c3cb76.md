Confirmed: `EcdsaBeefy.sol` has no upper bound on `AuthoritySetCommitment.len` (authority set size), and its per-signature loop cost in `verifyMmrUpdateProof` scales linearly (in fact the required signature count scales with `authoritySet.len` via `checkParticipationThreshold`). This is a direct structural analog to the Gravity Bridge `makeCheckpoint` gas-DoS finding.### Title
Unbounded BEEFY authority set size can permanently exceed block gas limit, freezing `EcdsaBeefy` consensus updates - (File: `evm/src/consensus/EcdsaBeefy.sol`)

### Summary
`EcdsaBeefy.verifyMmrUpdateProof` requires a strict supermajority (`2/3 + 1`) of ECDSA signatures from the current relay-chain authority set, and loops once per submitted signature performing `ECDSA.recover` plus a merkle-leaf hash, before running a `MerkleMultiProof.VerifyProof` over all of those leaves. Neither the contract nor `Types.AuthoritySetCommitment` enforces any upper bound on `authoritySet.len`. This is the same bug class as the Gravity Bridge finding: as the relay chain's authority set grows, the number of required signatures (and thus the gas cost of a single `verify` call) grows linearly and unboundedly, with no cap ever enforced on-chain.

### Finding Description
`verifyMmrUpdateProof` (`evm/src/consensus/EcdsaBeefy.sol:122-172`) computes:
```solidity
uint256 sigLen = relayProof.signedCommitment.votes.length;
...
if (!checkParticipationThreshold(sigLen, authoritySet.len)) revert SuperMajorityRequired();
...
for (uint256 i = 0; i < sigLen; i++) {
    Vote memory vote = relayProof.signedCommitment.votes[i];
    address authority = ECDSA.recover(commitmentHash, vote.signature);
    authorities[i] = MerkleMultiProof.Leaf({...});
}
bool valid = MerkleMultiProof.VerifyProof(authoritySet.root, relayProof.proof, authorities, authoritySet.len);
``` [1](#0-0) 

`checkParticipationThreshold` enforces `len >= (2*total)/3 + 1` [2](#0-1) , meaning a submitter cannot supply fewer signatures than that supermajority threshold relative to `authoritySet.len` — the number of signatures (and hence `ecrecover` calls, hashing, and merkle-multi-proof verification work) is *forced* to scale with the size of the relay chain's authority set. There is no `MAX_AUTHORITIES`/cap check anywhere in `EcdsaBeefy.sol`, `Types.sol`, or the `ConsensusRouter` that routes to it [3](#0-2) . The relay chain's own validator/authority set size is controlled entirely off-chain (governance of the relaying chain, e.g. Polkadot), and Hyperbridge's Solidity client has no way to reject an authority-set commitment update whose size makes the corresponding supermajority proof gas-unaffordable.

This mirrors the Gravity Bridge `makeCheckpoint` finding precisely: a validator/authority set that is permitted to grow arbitrarily large, combined with a mandatory linear-in-set-size verification loop and no cap, risks the on-chain verification transaction exceeding the block gas limit.

### Impact Explanation
If the trusted relay chain's BEEFY authority set grows large enough (e.g., during periods where the source chain's validator count increases), the `EcdsaBeefy` client's `verifyMmrUpdateProof` would require enough `ecrecover` + merkle-leaf operations that the transaction gas cost exceeds the network's block gas limit. Because `EcdsaBeefy.verify` is a `pure` function invoked from `ConsensusRouter.verify`, which is presumably called from `EvmHost`/`HandlerV2` consensus-update paths reachable by any relayer submitting a consensus proof, this would make it permanently impossible to advance the BEEFY consensus state via the ECDSA path. Since consensus-state advancement gates all subsequent state-commitment verification and message delivery for that route, this would freeze cross-chain message delivery for any chain relying on this consensus client, until/unless the authority set shrinks again (which is not guaranteed and may never happen). This is a permanent freezing-of-funds/freezing-of-messaging risk consistent with a Medium-severity finding, matching the accepted impact category ("route unable to deliver messages").

Note: The protocol does provide an alternative `SP1Beefy` verifier that offloads signature verification to a zk proof and is documented as "more gas-efficient for large authority sets" [4](#0-3) , which somewhat mitigates the overall protocol risk if deployments route through SP1 instead of ECDSA. However, `EcdsaBeefy` itself remains vulnerable to the same unbounded-gas freezing pattern as Gravity Bridge whenever it is the active/only consensus client for a given chain.

### Likelihood Explanation
Likelihood is bounded by how large a relay chain's authority set can realistically grow and how much gas per validator signature costs (`ecrecover` ~3000 gas, plus hashing and merkle proof steps). For typical relay-chain authority set sizes today, this may not be exploitable, but there is no protocol-enforced upper bound guaranteeing safety against future growth, unlike, e.g., the sync-committee verifier which is fixed at `SYNC_COMMITTEE_SIZE` (512) validators [5](#0-4) . Because BEEFY authority set growth is controlled by the relay chain's own governance (external to Hyperbridge), Hyperbridge has no lever to prevent this precondition, making it a legitimate, if slow-moving, freezing risk rather than a purely theoretical one.

### Recommendation
- Add an explicit maximum authority-set size (`MAX_AUTHORITY_SET_LEN`) enforced when a new `AuthoritySetCommitment` is accepted in `verifyMmrUpdateProof`, rejecting any BEEFY `nextAuthoritySet` update whose `len` exceeds a gas-safe bound.
- Alternatively/additionally, require or default all deployments serving chains with growing authority sets to use `SP1Beefy` (or another O(1)-gas verifier) instead of `EcdsaBeefy`, and consider deprecating `EcdsaBeefy` as authority sets grow past a safe threshold.
- Add monitoring/alerting on authority-set size trends so operators can migrate before gas costs approach block limits.

### Proof of Concept
Conceptual illustration (cannot be executed without a live BEEFY relay chain fork):
1. Assume a relay chain authority set grows to `N` validators such that `(2N/3)+1` signatures require more combined gas (ecrecover + hashing + merkle-multi-proof verification) than the target EVM chain's block gas limit.
2. A relayer submits a `RelayChainProof` with `sigLen = (2N/3)+1` votes to `ConsensusRouter.verify` → `EcdsaBeefy.verify` → `verifyMmrUpdateProof`.
3. The `for` loop at `evm/src/consensus/EcdsaBeefy.sol:154-159` performing `ECDSA.recover` per vote, combined with `MerkleMultiProof.VerifyProof` over `authoritySet.len` leaves, consumes gas exceeding the block gas limit.
4. The transaction cannot be mined; no valid update below the supermajority threshold is accepted (enforced by `checkParticipationThreshold`), so the consensus state can never advance, freezing all downstream message delivery relying on this `EcdsaBeefy` consensus client.

### Citations

**File:** evm/src/consensus/EcdsaBeefy.sol (L140-162)
```text
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

**File:** evm/src/consensus/EcdsaBeefy.sol (L241-243)
```text
    function checkParticipationThreshold(uint256 len, uint256 total) internal pure returns (bool) {
        return len >= ((2 * total) / 3) + 1;
    }
```

**File:** evm/src/consensus/ConsensusRouter.sol (L84-104)
```text
    function verify(bytes calldata previousState, bytes calldata encodedProof)
        external
        view
        returns (bytes memory, IntermediateState[] memory, uint256)
    {
        if (encodedProof.length == 0) revert EmptyProof();
        uint8 proofTypeByte = uint8(encodedProof[0]);

        if (proofTypeByte > uint8(type(ProofType).max)) {
            revert InvalidProofType(proofTypeByte);
        }

        ProofType proofType = ProofType(proofTypeByte);
        bytes calldata actualProof = encodedProof[1:];
        if (proofType == ProofType.Sp1) {
            return IConsensusV2(address(sp1Beefy)).verify(previousState, actualProof);
        } else if (proofType == ProofType.Ecdsa) {
            return IConsensusV2(address(ecdsaBeefy)).verify(previousState, actualProof);
        } else {
            revert InvalidProofType(proofTypeByte);
        }
```

**File:** docs/content/developers/evm/api/iconsensus.mdx (L194-203)
```text
### `SP1Beefy`
- Delegates signature verification to SP1 zkVM
- Verifies ZK proofs instead of individual signatures
- More gas-efficient for large authority sets
- Same security guarantees as EcdsaBeefy
- Requires the mmr leaf to be the one appended at the commitment's block
  (`parentNumber + 1 == blockNumber`). The zkVM proves only that the leaf is *in* the mmr,
  and an mmr is append-only, so this is enforced on-chain — otherwise a proof could advance
  the trusted height while replaying an older leaf's `nextAuthoritySet`
- Location: `SP1Beefy.sol`
```

**File:** modules/consensus/sync-committee/primitives/src/types.rs (L123-124)
```rust
	/// signature & participation bits
	pub sync_aggregate: SyncAggregate<SYNC_COMMITTEE_SIZE>,
```
