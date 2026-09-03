# Q5212: nullifier binding: no verifyingContract is mixed into the n [when the external action is Em]

## Question
Given that no verifyingContract is mixed into the nullifier, can an unprivileged attacker arrange that a nullifier from one Hinkal deployment is accepted by another on the same chain, so a commitment is either spent twice across contexts or a value-bearing leaf is left with no nullifier that will ever be recorded, specifically when the external action is Emporium with signerAddress zero (where the unsigned stateless op path runs)?

## Target
- File/function: circuits/NullifierCalculator.circom :: NullifierCalculator / HinkalBase.insertNullifiers
- Entrypoint: Hinkal.transact
- Attacker controls: nullifier fields in CircomData, chain/deployment context, commitment preimage
- Exploit idea: exploit missing domain separation or the zero-nullifier skip
- Invariant to test: one value-bearing leaf == one nullifier ever accepted for it (per chain and deployment)
- Expected Immunefi impact: Critical: spending a commitment twice / nullifier bypass (insolvency)
- Fast validation: Foundry: replay a nullifier across two deployments/chains, assert both spends succeed
