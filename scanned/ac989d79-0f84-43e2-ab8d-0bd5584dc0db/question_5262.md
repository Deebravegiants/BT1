# Q5262: nullifier binding: insertNullifiers skips entries equal to  [when the external action is Em]

## Question
Given that insertNullifiers skips entries equal to 0, can an unprivileged attacker arrange that a crafted spend leaves the nullifier unrecorded and re-spendable, so a commitment is either spent twice across contexts or a value-bearing leaf is left with no nullifier that will ever be recorded, specifically when the external action is Emporium with signerAddress zero (where the unsigned stateless op path runs)?

## Target
- File/function: circuits/NullifierCalculator.circom :: NullifierCalculator / HinkalBase.insertNullifiers
- Entrypoint: Hinkal.transact
- Attacker controls: nullifier fields in CircomData, chain/deployment context, commitment preimage
- Exploit idea: exploit missing domain separation or the zero-nullifier skip
- Invariant to test: one value-bearing leaf == one nullifier ever accepted for it (per chain and deployment)
- Expected Immunefi impact: Critical: spending a commitment twice / nullifier bypass (insolvency)
- Fast validation: Foundry: replay a nullifier across two deployments/chains, assert both spends succeed
