# Q2252: subset via supply-collateral-add: credit one side of an accounting pair without the other

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls vault share price at the moment of the deposit leg reach `subset` (mainnet/contracts/market/v0-market-vault.clar:100) in a state where it credit one side of an accounting pair without the other? Given that it tests bitmask containment, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `subset` tests bitmask containment. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with vault share price at the moment of the deposit leg varied, and assert that the value `subset` returns is identical in both runs; a divergence confirms the finding.
