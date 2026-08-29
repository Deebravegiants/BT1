# Q2621: zip via collateral-remove-redeem: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling `receiver` for the underlying leg, drive `zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) — which pairs the utilization and rate point lists element by element — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `collateral-remove-redeem` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-remove-redeem` call, then the attacker-shaped one with `receiver` for the underlying leg, and assert the attacker's net token balance change is zero or negative.
