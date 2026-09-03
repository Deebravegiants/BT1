# Q1869: historical root acceptance: use rootHashHinkalIndex == m_index-1 bou [at the maximum allowed array l]

## Question
Can an unprivileged attacker use rootHashHinkalIndex == m_index-1 boundary vs the stored roots mapping off-by-one, given rootHashExists accepts any stored historical root, to prove inclusion of a commitment under a root where it should not exist or bypass the index bounds, specifically at the maximum allowed array lengths (where boundary sizing exposes off-by-one behaviour)?

## Target
- File/function: contracts/MerkleBase.sol :: rootHashExists / getRootHash
- Entrypoint: Hinkal.transact
- Attacker controls: rootHashHinkal, rootHashHinkalIndex
- Exploit idea: pick a stored root/index pair that admits an inclusion proof it should not
- Invariant to test: a proof under roots[index] is valid only for leaves inserted at or before that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Hardhat+snarkjs: prove under a stale root for a later leaf, assert acceptance
