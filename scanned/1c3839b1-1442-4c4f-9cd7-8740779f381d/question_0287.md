# Q0287: nullifier binding: NullifierCalculator zeroes the output wh [across a batch of transactions]

## Question
Given that NullifierCalculator zeroes the output when commitment == 0, can an unprivileged attacker arrange that a zero-commitment input yields nullifier 0 which insertNullifiers skips, so a commitment is either spent twice across contexts or a value-bearing leaf is left with no nullifier that will ever be recorded, specifically across a batch of transactions landing in one block (where batching and ordering change the observable pre/post state)?

## Target
- File/function: circuits/NullifierCalculator.circom :: NullifierCalculator / HinkalBase.insertNullifiers
- Entrypoint: Hinkal.transact
- Attacker controls: nullifier fields in CircomData, chain/deployment context, commitment preimage
- Exploit idea: exploit missing domain separation or the zero-nullifier skip
- Invariant to test: one value-bearing leaf == one nullifier ever accepted for it (per chain and deployment)
- Expected Immunefi impact: Critical: spending a commitment twice / nullifier bypass (insolvency)
- Fast validation: Foundry: replay a nullifier across two deployments/chains, assert both spends succeed
