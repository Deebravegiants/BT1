# Q0936: transfer_allow_death threshold handling can create dust or hidden debt

## Question
Can an unprivileged attacker choose amounts, fees, or prices, beneficiary, delegate, or target accounts around a minimum-balance, deposit, fee, or rounding threshold in `transfer_allow_death` so the pallet leaves spendable dust or an unpaid liability behind?

## Target
- File/function: substrate/frame/balances/src/lib.rs::transfer_allow_death
- Entrypoint: signed extrinsic `transfer_allow_death`
- Attacker controls: amounts, fees, or prices, beneficiary, delegate, or target accounts
- Exploit idea: Probe exact equality, off-by-one, and precision truncation cases around the pallet's economic thresholds.
- Invariant to test: Threshold transitions must not create accounts, shares, credits, or debts that violate the pallet's own liveness and solvency rules.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: Fuzz threshold-1 / threshold / threshold+1 values and assert no residual state becomes spendable or unrecoverable.
