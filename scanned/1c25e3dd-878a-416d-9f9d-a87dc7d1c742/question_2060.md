# Q2060: debt-add-scaled via transfer: credit one side of an accounting pair without the other

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the destination principal, including the market, the market-vault or the treasury reach `debt-add-scaled` (mainnet/contracts/market/v0-market-vault.clar:442) in a state where it credit one side of an accounting pair without the other? Given that it stamps `last-borrow-block` from `stacks-block-height` onto the named ACCOUNT, not the caller, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:442` -> `debt-add-scaled`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `debt-add-scaled` stamps `last-borrow-block` from `stacks-block-height` onto the named ACCOUNT, not the caller. Reach it through `transfer` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with the destination principal, including the market, the market-vault or the treasury varied, and assert that the value `debt-add-scaled` returns is identical in both runs; a divergence confirms the finding.
