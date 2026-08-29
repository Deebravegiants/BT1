# Q5060: collateral-remove via transfer: record a repayment larger than the value actually delivere

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the destination principal, including the market, the market-vault or the treasury reach `collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) in a state where it record a repayment larger than the value actually delivered? Given that it decrements the map and writes the entry before `send-tokens` executes, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `transfer` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with the destination principal, including the market, the market-vault or the treasury varied, and assert that the value `collateral-remove` returns is identical in both runs; a divergence confirms the finding.
