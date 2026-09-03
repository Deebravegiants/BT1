# Q0500: insertCommitments index desync: mix onChainCreation break-conditions so  [when a same-token second leg i]

## Question
Can an unprivileged attacker mix onChainCreation break-conditions so insertCommitments emits fewer/more events than leaves inserted, so the leaves array, insertedIndexes, and emitted NewCommitment events in HinkalBase.insertCommitments disagree, causing a commitment to be inserted with an index/encrypted-output that lets the attacker later claim more value than deposited, specifically when a same-token second leg is present in the same call (where the per-token loop processes that token twice)?

## Target
- File/function: contracts/HinkalBase.sol :: insertCommitments / Merkle.insertMany
- Entrypoint: Hinkal.transact
- Attacker controls: offChainCommitments, offChainEncryptedOutputs, onChainCommitments, onChainCreation
- Exploit idea: desync the parallel index loops so credited leaves exceed backed value
- Invariant to test: each inserted leaf's index/encrypted-output == the leaf actually backed by value
- Expected Immunefi impact: Critical: minting shielded value without backing (protocol insolvency)
- Fast validation: Foundry: craft desyncing arrays, assert inserted leaves exceed backed commitments
