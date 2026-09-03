# Q2069: historical root acceptance: spend against a root from before your ow [when the external action retur]

## Question
Can an unprivileged attacker spend against a root from before your own deposit was included, given rootHashExists accepts any stored historical root, to prove inclusion of a commitment under a root where it should not exist or bypass the index bounds, specifically when the external action returns an empty UTXO set (where utxoAmount is zero while value still moved)?

## Target
- File/function: contracts/MerkleBase.sol :: rootHashExists / getRootHash
- Entrypoint: Hinkal.transact
- Attacker controls: rootHashHinkal, rootHashHinkalIndex
- Exploit idea: pick a stored root/index pair that admits an inclusion proof it should not
- Invariant to test: a proof under roots[index] is valid only for leaves inserted at or before that index
- Expected Immunefi impact: Critical: proof or verifier bypass (unproven state accepted)
- Fast validation: Hardhat+snarkjs: prove under a stale root for a later leaf, assert acceptance
