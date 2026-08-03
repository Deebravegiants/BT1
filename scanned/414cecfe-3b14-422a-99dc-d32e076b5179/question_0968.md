# Q0968: claim_payout threshold handling can create dust or hidden debt

## Question
Can an unprivileged attacker choose call repetition, batching order, and surrounding state around a minimum-balance, deposit, fee, or rounding threshold in `claim_payout` so the pallet leaves spendable dust or an unpaid liability behind?

## Target
- File/function: substrate/frame/nomination-pools/src/lib.rs::claim_payout
- Entrypoint: signed extrinsic `claim_payout`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Probe exact equality, off-by-one, and precision truncation cases around the pallet's economic thresholds.
- Invariant to test: Threshold transitions must not create accounts, shares, credits, or debts that violate the pallet's own liveness and solvency rules.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Fuzz threshold-1 / threshold / threshold+1 values and assert no residual state becomes spendable or unrecoverable.
