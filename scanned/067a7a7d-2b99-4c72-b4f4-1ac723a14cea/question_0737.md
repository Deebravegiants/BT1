# Q0737: nullifier binding: NullifierCalculator zeroes the output wh [when a prior tx in the same bl]

## Question
Given that NullifierCalculator zeroes the output when commitment == 0, can an unprivileged attacker arrange that a zero-commitment input yields nullifier 0 which insertNullifiers skips, so a commitment is either spent twice across contexts or a value-bearing leaf is left with no nullifier that will ever be recorded, specifically when a prior tx in the same block left the action or tree in a partial state (where cross-tx residual state carries over)?

## Target
- File/function: circuits/NullifierCalculator.circom :: NullifierCalculator / HinkalBase.insertNullifiers
- Entrypoint: Hinkal.transact
- Attacker controls: nullifier fields in CircomData, chain/deployment context, commitment preimage
- Exploit idea: exploit missing domain separation or the zero-nullifier skip
- Invariant to test: one value-bearing leaf == one nullifier ever accepted for it (per chain and deployment)
- Expected Immunefi impact: Critical: spending a commitment twice / nullifier bypass (insolvency)
- Fast validation: Foundry: replay a nullifier across two deployments/chains, assert both spends succeed
