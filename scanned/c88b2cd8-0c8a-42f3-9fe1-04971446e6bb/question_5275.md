# Q5275: insertCommitments index desync: exploit the -1*index sign convention on  [when the external action is Em]

## Question
Can an unprivileged attacker exploit the -1*index sign convention on on-chain commitments to confuse off-chain indexers into miscrediting, so the leaves array, insertedIndexes, and emitted NewCommitment events in HinkalBase.insertCommitments disagree, causing a commitment to be inserted with an index/encrypted-output that lets the attacker later claim more value than deposited, specifically when the external action is Emporium with signerAddress zero (where the unsigned stateless op path runs)?

## Target
- File/function: contracts/HinkalBase.sol :: insertCommitments / Merkle.insertMany
- Entrypoint: Hinkal.transact
- Attacker controls: offChainCommitments, offChainEncryptedOutputs, onChainCommitments, onChainCreation
- Exploit idea: desync the parallel index loops so credited leaves exceed backed value
- Invariant to test: each inserted leaf's index/encrypted-output == the leaf actually backed by value
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: craft desyncing arrays, assert inserted leaves exceed backed commitments
