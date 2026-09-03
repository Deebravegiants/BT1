# Q2376: nullifier binding: DepositOnChainUtxos stamps timeStamp = c [when the same proof is reused ]

## Question
Given that DepositOnChainUtxos stamps timeStamp = circomData.timeStamp + utxoIndex, can an unprivileged attacker arrange that the caller forces a commitment colliding with an existing leaf, so a commitment is either spent twice across contexts or a value-bearing leaf is left with no nullifier that will ever be recorded, specifically when the same proof is reused with only calldata mutated (where the proof-to-calldata binding is stressed)?

## Target
- File/function: circuits/NullifierCalculator.circom :: NullifierCalculator / HinkalBase.insertNullifiers
- Entrypoint: Hinkal.transact
- Attacker controls: nullifier fields in CircomData, chain/deployment context, commitment preimage
- Exploit idea: exploit missing domain separation or the zero-nullifier skip
- Invariant to test: one value-bearing leaf == one nullifier ever accepted for it (per chain and deployment)
- Expected Immunefi impact: Critical: spending a commitment twice / nullifier bypass (insolvency)
- Fast validation: Foundry: replay a nullifier across two deployments/chains, assert both spends succeed
