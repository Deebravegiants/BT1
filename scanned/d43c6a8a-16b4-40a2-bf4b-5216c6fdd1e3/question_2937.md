# Q2937: nullifier binding: no chainId is mixed into the nullifier w [when the token is a fee-on-tra]

## Question
Given that no chainId is mixed into the nullifier while signedMessageHash includes block.chainid, can an unprivileged attacker arrange that a nullifier valid on Base is replayed on Arbitrum for the same commitment preimage, so a commitment is either spent twice across contexts or a value-bearing leaf is left with no nullifier that will ever be recorded, specifically when the token is a fee-on-transfer token (where delivered amount is below the stated amount)?

## Target
- File/function: circuits/NullifierCalculator.circom :: NullifierCalculator / HinkalBase.insertNullifiers
- Entrypoint: Hinkal.transact
- Attacker controls: nullifier fields in CircomData, chain/deployment context, commitment preimage
- Exploit idea: exploit missing domain separation or the zero-nullifier skip
- Invariant to test: one value-bearing leaf == one nullifier ever accepted for it (per chain and deployment)
- Expected Immunefi impact: Critical: spending a commitment twice / nullifier bypass (insolvency)
- Fast validation: Foundry: replay a nullifier across two deployments/chains, assert both spends succeed
