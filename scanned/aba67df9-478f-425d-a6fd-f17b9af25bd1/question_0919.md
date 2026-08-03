# Q0919: set_reserves threshold handling can create dust or hidden debt

## Question
Can an unprivileged attacker choose IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering around a minimum-balance, deposit, fee, or rounding threshold in `set_reserves` so the pallet leaves spendable dust or an unpaid liability behind?

## Target
- File/function: substrate/frame/assets/src/lib.rs::set_reserves
- Entrypoint: signed extrinsic `set_reserves`
- Attacker controls: IDs, hashes, nonces, or location fields, duplicate or adversarial list ordering
- Exploit idea: Probe exact equality, off-by-one, and precision truncation cases around the pallet's economic thresholds.
- Invariant to test: Threshold transitions must not create accounts, shares, credits, or debts that violate the pallet's own liveness and solvency rules.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Fuzz threshold-1 / threshold / threshold+1 values and assert no residual state becomes spendable or unrecoverable.
