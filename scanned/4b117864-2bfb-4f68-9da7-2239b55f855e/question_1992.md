# Q1992: calc-principal-ratio-reduction via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls the zToken/underlying id mapping reached (the u100 sentinel branch) reach `calc-principal-ratio-reduction` (mainnet/contracts/vault/v0-vault-stx.clar:191) in a state where it credit one side of an accounting pair without the other? Given that it reduces scaled principal proportionally to an amount over total debt, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:191` -> `calc-principal-ratio-reduction`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `calc-principal-ratio-reduction` reduces scaled principal proportionally to an amount over total debt. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the zToken/underlying id mapping reached (the u100 sentinel branch) across its boundary values through `collateral-remove-redeem` in simnet and assert `calc-principal-ratio-reduction` never returns a value that breaks the invariant.
