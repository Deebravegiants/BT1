### Title
Untagged leaf/internal-node hashing combined with relayer-supplied `total_leaves` in BEEFY parachain-header Merkle proof enables forged finality proofs - (File: `modules/consensus/beefy/verifier/src/lib.rs`)

### Summary
The BEEFY consensus verifier's parachain-header inclusion check (`verify_parachain_headers`) and its Solidity twin (`EcdsaBeefy.verifyParachainHeaderProof`) rebuild a Merkle root from relayer-supplied leaves and a relayer-supplied leaf count, using a Merkle-tree hash scheme that — exactly like the pre-CVE-2017-12842 Bitcoin design — never tags leaf hashes differently from internal-node hashes. The tree-shape/leaf-count value that anchors the proof's structure is not derived from any trusted, independently-known source; it is taken straight from the untrusted `ConsensusMessage`/`RelayChainProof` submitted by the relayer.

### Finding Description
`verify_parachain_headers` computes each leaf as `H::keccak256(&(para_id, header).encode())` and verifies with `rs_merkle`: [1](#0-0) 

Internal nodes in the same tree are produced by plain concatenation-then-hash (`MerkleHasher<H>::hash` is reused for every layer, and the MMR/merkle merge functions used elsewhere in the codebase are likewise `keccak256(left||right)` with no leaf/node domain separator): [2](#0-1) 

Because leaf hashes and internal-node hashes live in the exact same hash space (no leaf-prefix / node-prefix tagging), any keccak256 output that is a genuine internal node of the real parachain-heads tree is *indistinguishable*, at verification time, from a genuine leaf hash. The only thing standing between "this 32-byte value is an internal node" and "this 32-byte value is a leaf for parachain X" is the caller-supplied `total_leaves` count, which fixes where the tree boundary between leaf-layer and internal layers falls: [3](#0-2) 

`parachain_proof.total_leaves` originates from the prover/relayer-controlled `ParachainProof` and is never checked against any value the verifier can derive independently (unlike the sibling authority-membership check in the same function, `verify_mmr_update_proof`, which correctly anchors `total_leaves` to the trusted, chain-stored `authority_set.len`): [4](#0-3) 

The prover builds this proof from the real `rs_merkle::MerkleTree` with no independent binding either: [5](#0-4) 

The Solidity path has the identical shape — `MerkleMultiProof.VerifyProof` is called with a relayer-controlled `proof.leafCount`: [6](#0-5) 

This is precisely the bug class in the referenced report: Bitcoin's original Merkle tree does not distinguish a transaction leaf hash from an internal node hash, so a value that is honestly an internal node of the real tree can be replayed as a fabricated "leaf" for a payment/tx that never happened, because the verifier has no independently-trusted notion of "how many real items exist at the leaf layer." The docs for this codebase explicitly describe the general second-preimage mitigation ("the verifier must independently know the number of items in the tree"): [7](#0-6) 

but the mitigation is not applied here: `total_leaves`/`leafCount` is *not* independently known by the verifier — it is taken from the same untrusted message that supplies the proof itself, so a relayer can freely choose the leaf/internal boundary that best lets them reuse a real internal-node hash from the authentic `leaf_extra` tree as a forged "parachain header leaf" for an arbitrary `para_id`/header pair whose SCALE-encoded keccak256 preimage they can find.

### Impact Explanation
A successful forgery lets a relayer present, and have the light client accept, a `StateCommitment` for a parachain state that the relay chain never actually finalized at that height. Downstream, `verify_parachain_headers`' output feeds directly into ISMP state-commitment storage used by `handle_unsigned`/message delivery and GET-response construction, so a forged commitment can be leveraged for unsound state commitment acceptance and forged message delivery (e.g. proving membership of a request/response that was never posted on the claimed parachain) — matching the "ostensibly valid proof for a payment/event that did not occur" characterization of CVE-2017-12842.

### Likelihood Explanation
Exploitation requires finding a second preimage under `keccak256(SCALE_encode(para_id, header))` that collides with a specific 32-byte internal-node value from the real tree — a computationally expensive (but not domain-tag-protected) search, consistent with the original CVE's own framing ("would cost more than a million dollars"). It is not a cheap, everyday attack, but it is a real cryptographic weakness reachable from a single relayed `ConsensusMessage`/`RelayChainProof` submitted by any unprivileged relayer, with no additional trust assumptions required beyond what a relayer already has.

### Recommendation
Bind `total_leaves`/`leafCount` for the parachain-header proof to a value the verifier can independently trust (e.g., commit the parachain leaf count itself inside the signed MMR leaf/commitment, the same way `authority_set.len` anchors the authority-membership proof), and/or introduce domain-separated (tagged) hashing so that leaf hashes and internal-node hashes can never be confused, regardless of what leaf count a relayer claims.

### Proof of Concept
1. Relayer observes a legitimate BEEFY commitment whose `leaf_extra` parachain-heads tree contains some internal node `N = keccak256(L || R)` at depth `d`, built honestly by `build_parachain_proof`.
2. Relayer searches offline for `header` bytes such that `keccak256(SCALE_encode(target_para_id, header)) == N` (a second-preimage search over the space of internal nodes reachable from the true tree — many internal nodes to target increases attack surface, similar to Bitcoin's birthday-style leaf/node confusion).
3. Relayer submits a `ConsensusMessage` whose `ParachainProof.total_leaves` is chosen so that `N`'s position lines up as a leaf slot for `target_para_id`, with `proof` hashes taken from the real tree at depth `d`'s siblings.
4. `verify_parachain_headers` recomputes the same real root (`heads_root`) using the forged leaf plus genuine sibling hashes and accepts the header for `target_para_id` as finalized, even though it was never included by the relay chain.

### Citations

**File:** modules/consensus/beefy/verifier/src/lib.rs (L67-86)
```rust
impl<H: Keccak256> Hasher for MerkleHasher<H> {
	type Hash = [u8; 32];

	fn hash(data: &[u8]) -> Self::Hash {
		H::keccak256(data).into()
	}
}

/// Merge strategy for the merkle mountain range crate, generic over the hash function
struct KeccakMerge<H>(PhantomData<H>);

impl<H: Keccak256> MmrMerge for KeccakMerge<H> {
	type Item = [u8; 32];

	fn merge(left: &Self::Item, right: &Self::Item) -> Result<Self::Item, MmrError> {
		let mut data = [0u8; 64];
		data[..32].copy_from_slice(left);
		data[32..].copy_from_slice(right);
		Ok(H::keccak256(&data).into())
	}
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L164-171)
```rust
	let merkle_proof = MerkleProof::<MerkleHasher<H>>::new(mmr.authority_proof.clone());

	let valid = merkle_proof.verify(
		authority_set.keyset_commitment.into(),
		&authority_indices,
		&authority_leaves,
		authority_set.len as usize,
	);
```

**File:** modules/consensus/beefy/verifier/src/lib.rs (L198-216)
```rust
	let mut indexed_leaf_hashes = Vec::with_capacity(parachain_proof.parachains.len());

	for para_header in &parachain_proof.parachains {
		let leaf = (para_header.para_id, para_header.header.clone());
		let hash: [u8; 32] = H::keccak256(&leaf.encode()).into();
		indexed_leaf_hashes.push((para_header.index as usize, hash));
	}

	indexed_leaf_hashes.sort_by_key(|(index, _)| *index);

	let (leaf_indices, leaf_hashes): (Vec<usize>, Vec<[u8; 32]>) =
		indexed_leaf_hashes.into_iter().unzip();
	let merkle_proof = MerkleProof::<MerkleHasher<H>>::new(parachain_proof.proof.clone());
	let valid = merkle_proof.verify(
		heads_root.0,
		&leaf_indices,
		&leaf_hashes,
		parachain_proof.total_leaves as usize,
	);
```

**File:** modules/consensus/beefy/prover/src/lib.rs (L118-144)
```rust
/// Build the parachain header merkle proof from the heads committed in an MMR leaf.
fn build_parachain_proof(para_ids: &[u32], heads: &[(u32, Vec<u8>)]) -> ParachainProof {
	let leaves: Vec<[u8; 32]> = heads.iter().map(|pair| keccak_256(&pair.encode())).collect();
	let leaf_count = leaves.len();

	let indices: Vec<usize> = para_ids
		.iter()
		.map(|id| heads.iter().position(|(i, _)| *i == *id).expect("ParaId should exist"))
		.collect();

	let tree = rs_merkle::MerkleTree::<util::MerkleHasher>::from_leaves(&leaves);
	let para_proof = tree.proof(&indices);

	let mut parachains: Vec<_> = indices
		.iter()
		.map(|&i| ParachainHeader {
			header: heads[i].1.clone(),
			index: i as u32,
			para_id: heads[i].0,
		})
		.collect();
	parachains.sort_by_key(|p| p.index);

	let proof = para_proof.proof_hashes().to_vec();

	ParachainProof { parachains, proof, total_leaves: leaf_count as u32 }
}
```

**File:** evm/src/consensus/EcdsaBeefy.sol (L198-229)
```text
    // @dev Verifies that some parachain header has been finalized, given the current trusted consensus state.
    function verifyParachainHeaderProof(bytes32 headsRoot, ParachainProof memory proof)
        internal
        pure
        returns (IntermediateState[] memory)
    {
        uint256 len = proof.parachains.length;
        MerkleMultiProof.Leaf[] memory leaves = new MerkleMultiProof.Leaf[](len);
        IntermediateState[] memory intermediates = new IntermediateState[](len);

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

        if (len > 0) {
            bool valid = MerkleMultiProof.VerifyProof(headsRoot, proof.proof, leaves, proof.leafCount);
            if (!valid) revert InvalidMmrProof();
        }

        return intermediates;
    }
```

**File:** docs/content/protocol/cryptography/merkle-trees/binary.mdx (L76-80)
```text
## Second Pre-image Attacks

[Second pre-image attacks](https://en.wikipedia.org/wiki/Merkle_tree#Second_preimage_attack) arise when merkle tree proof schemes do not check the tree depth when verifying merkle proofs. This allows for attackers to construct either arbitrarily deep or shallow trees that have the same root hash as the verifier’s, in order to fool the verifier that some forged items are in the original tree.

In order to mitigate this, given our current proof scheme, **it is necessary that the verifier knows the number of items in the tree**. The height of the tree can be computed from it's leaf count and compared to the length of the 2D proof array (which encodes the height of the tree). If they do not match then the proof can safely be rejected because it describes a different tree and is  attempting to perform a pre-image collision attack.
```
