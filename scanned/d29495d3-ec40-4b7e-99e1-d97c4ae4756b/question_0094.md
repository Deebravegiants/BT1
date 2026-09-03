# Q0094: historical root acceptance: exploit that getRootHash returns 0 when 

## Question
Can an unprivileged attacker exploit that getRootHash returns 0 when empty so a 0 root is accepted early, given rootHashExists accepts any stored historical root, to prove inclusion of a commitment under a root where it should not exist or bypass the index bounds?

## Target
- File/function: contracts/MerkleBase.sol :: rootHashExists / getRootHash
- Entrypoint: Hinkal.transact
- Attacker controls: rootHashHinkal, rootHashHinkalIndex
- Exploit idea: pick a stored root/index pair that admits an inclusion proof it should not
- Invariant to test: a proof under roots[index] is valid only for leaves inserted at or before that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Hardhat+snarkjs: prove under a stale root for a later leaf, assert acceptance
