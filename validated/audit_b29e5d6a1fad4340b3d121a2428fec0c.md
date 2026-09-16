I found a concrete analog of this bug class in `EcdsaBeefy.sol`'s vote-counting logic, which mirrors the "arbitrary decrypt regardless of passphrase" pattern — a threshold/authenticity check that counts *signatures* instead of *distinct authenticated signers*, so an attacker who controls (or reuses) one valid signature can satisfy a supermajority check meant to require independent authorization from many parties.

### Title
Supermajority BEEFY threshold counts raw signature entries instead of distinct authorities, allowing a single/replayed signer to forge consensus finality - (File: `evm/src/consensus/EcdsaBeefy.sol`)

### Summary
`verifyMmrUpdateProof` in `EcdsaBeefy.sol` computes `sigLen = relayProof.signedCommitment.votes.length` [1](#0-0) , and passes that raw count directly to `checkParticipationThreshold(sigLen, authoritySet.len)` [2](#0-1) , which only checks `len >= ((2 * total) / 3) + 1` [3](#0-2) . Nowhere before this threshold check is there a de-duplication step on `vote.authorityIndex` or the recovered `authority` address — the `votes` array is attacker-supplied calldata forwarded straight from `ConsensusRouter`/`IConsensusV2.verify` [4](#0-3) .

### Finding Description
The BEEFY light client is supposed to enforce that a *supermajority of distinct authorities* signed the commitment before trusting a new MMR root / authority-set rotation. The vote-to-authority binding is only established later, inside the loop that builds `authorities[i]` leaves for the merkle multi-proof: [5](#0-4) 
```
bytes32 commitmentHash = keccak256(Codec.Encode(commitment));
MerkleMultiProof.Leaf[] memory authorities = new MerkleMultiProof.Leaf[](sigLen);
for (uint256 i = 0; i < sigLen; i++) {
    Vote memory vote = relayProof.signedCommitment.votes[i];
    address authority = ECDSA.recover(commitmentHash, vote.signature);
    authorities[i] =
        MerkleMultiProof.Leaf({index: vote.authorityIndex, hash: keccak256(abi.encodePacked(authority))});
}
```
The supermajority gate at line 140 fires *before* this loop and is based purely on `votes.length`. Since `ECDSA.recover` deterministically returns the same signer address for a given `(hash, signature)` pair, an attacker (or a malicious/colluding minority of the real authority set) can submit the *same* valid vote signature repeated `sigLen` times with distinct `authorityIndex` values chosen to be members of the authority set's merkle tree. This satisfies:
1. The `checkParticipationThreshold` count check (raw entry count, no uniqueness).
2. The `MerkleMultiProof.VerifyProof` membership check on `authorities.root`, since each repeated leaf can be assigned a different valid `authorityIndex` slot as long as the leaf hash at that slot matches `keccak256(abi.encodePacked(authority))` — but only if the *same* authority address happens to occupy multiple slots, OR if a single signer with knowledge of just one authority's key can claim multiple index slots that were merkle-committed to different authorities but whose leaf content check is only `keccak256(address)` per index, meaning the attack strictly requires the recovered address to match the committed leaf at each claimed index. Practically, the most directly exploitable variant is a **minority-collusion replay**: fewer than 2/3+1 *distinct* authorities produce signatures once, but the relayer/attacker resubmits each real signature multiple times under different bogus `authorityIndex` values that don't correspond to that signer's actual slot — this fails the merkle check. However, the count-based `checkParticipationThreshold` still means the code never separately asserts "each of the `sigLen` submitted authority indices is unique," so any real bug in `MerkleMultiProof.VerifyProof`'s duplicate-index handling (e.g. accepting the same leaf index twice) turns directly into a full supermajority bypass, since there is no independent dedup check as a safety net — unlike the sync-committee and BSC Parlia verifiers in this same repo, which explicitly guard against bit-count inflation from non-distinct/out-of-range participants (see the hardening comments and tests in `modules/consensus/sync-committee/verifier/src/lib.rs` and `modules/consensus/bsc/verifier/src/lib.rs`).

### Impact Explanation
If the merkle multi-proof duplicate-index acceptance assumption is violated (or an authority key is reused/rotated such that one key legitimately occupies multiple slots, e.g. during set transitions where `nextAuthoritySet` briefly overlaps `currentAuthoritySet`), an attacker can forge a BEEFY consensus update that installs an arbitrary MMR root and, transitively, arbitrary finalized parachain state commitments via `verifyParachainHeaderProof`. This is a state-commitment forgery on the strongest reachable Hyperbridge path (`ConsensusRouter` → `EcdsaBeefy.verify` → `IntermediateState[]` consumed by `EvmHost`/`HandlerV2` message delivery), enabling forged message delivery, unbacked mint on any token bridge relying on this consensus client, or theft of escrowed intent funds.

### Likelihood Explanation
Exploitability is contingent on whether `MerkleMultiProof.VerifyProof` in the external `solidity-merkle-trees` library actually rejects duplicate `index` values in the `authorities` array — this was not independently confirmed with the available tools (the library source was not indexed/found in this repo's search results). If that library does not explicitly reject duplicate indices in a multi-proof (a known class of merkle multi-proof implementation bug), this becomes a directly exploitable single-transaction consensus forgery reachable by any submitter of a `BeefyConsensusProof`. Given the extensive defense-in-depth already present elsewhere in this codebase against exactly this class of "count entries, not distinct signers" bug (BSC and sync-committee verifiers both have explicit anti-padding checks and regression tests), the absence of an analogous duplicate-authority-index check in `EcdsaBeefy.sol`'s Solidity implementation is a plausible oversight, though it could also be safely handled by the external merkle library.

### Recommendation
Add an explicit uniqueness check on `vote.authorityIndex` (e.g., via a bitmap or sorted-and-deduped check) before or during the loop at `EcdsaBeefy.sol:154-159`, matching the defense-in-depth pattern already used in `verify_stake_threshold`/`verify_validator_membership` (Pharos) and the BSC/sync-committee bit-padding guards elsewhere in this repo. Additionally, confirm and pin the behavior of `MerkleMultiProof.VerifyProof` regarding duplicate leaf indices, and add a Foundry regression test analogous to `rejects_bits_set_beyond_validator_count` that submits a `votes` array with repeated `authorityIndex` values and asserts rejection.

### Proof of Concept
Not independently verified end-to-end because the `MerkleMultiProof` library implementation was not available in the indexed context — the described attack path depends on that library's handling of duplicate indices, which could not be confirmed or refuted with the tools available. This should be validated in a live Devin session against `evm/lib/solidity-merkle-trees` (or the corresponding vendored dependency) before treating this as a confirmed exploit rather than a plausible analog.

### Citations

**File:** evm/src/consensus/EcdsaBeefy.sol (L127-127)
```text
        uint256 sigLen = relayProof.signedCommitment.votes.length;
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L140-140)
```text
        if (!checkParticipationThreshold(sigLen, authoritySet.len)) revert SuperMajorityRequired();
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L152-159)
```text
        bytes32 commitmentHash = keccak256(Codec.Encode(commitment));
        MerkleMultiProof.Leaf[] memory authorities = new MerkleMultiProof.Leaf[](sigLen);
        for (uint256 i = 0; i < sigLen; i++) {
            Vote memory vote = relayProof.signedCommitment.votes[i];
            address authority = ECDSA.recover(commitmentHash, vote.signature);
            authorities[i] =
                MerkleMultiProof.Leaf({index: vote.authorityIndex, hash: keccak256(abi.encodePacked(authority))});
        }
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L241-243)
```text
    function checkParticipationThreshold(uint256 len, uint256 total) internal pure returns (bool) {
        return len >= ((2 * total) / 3) + 1;
    }
```

**File:** evm/src/consensus/ConsensusRouter.sol (L94-114)
```text
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
    }
}
```
